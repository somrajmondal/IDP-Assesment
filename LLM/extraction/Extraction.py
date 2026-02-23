import json
from fuzzywuzzy import fuzz
from utils.log import logger
import re
class Extraction:
    def __init__(self, document,model):
        """Initialize the Extraction class with a Document object."""
        self.document = document
        self.template_entities = []
        self.model = model  

    def extract_pages(self, ner_model):
        """Apply NER-based extraction to each page of the document and extract entities."""
        for page_number in range(1, self.document.num_pages + 1):
            page_content = f"Content of page {page_number}"  
            entities = ner_model.extract_entities(page_content)
            self.document.add_entities_to_page(page_number, entities)

   

    def clean_and_fix_json(self, json_string):
        try:
            # Step 1: Remove trailing commas before ] or }
            json_string = re.sub(r",\s*([\]}])", r"\1", json_string)

            # Step 2: Remove control characters (non-printable chars)
            json_string = re.sub(r'[\x00-\x1f\x7f]', '', json_string)

            # Step 3: Fix unterminated strings by adding missing closing quote at end of string values
            if re.search(r'":\s*"(?!.*")', json_string):
                json_string = re.sub(r'(":[^",\]}]*)$', r'\1"', json_string)

            # Step 4: Fix common missing commas
            json_string = re.sub(r'"\s*"\s*', '","', json_string)
            json_string = re.sub(r'"\s*{\s*"', '",{', json_string)
            json_string = re.sub(r'}\s*"', '},"', json_string)

            # Step 5: Try to parse
            return json_string

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error after cleanup attempt: {e}")
        
        # Step 6: Fallback line-by-line parsing
        fallback_dict = {}
        try:
            lines = json_string.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    fallback_dict[key.strip().strip('"')] = value.strip().strip('"')
            if fallback_dict:
                logger.info("Used fallback line-by-line parser.")
                return fallback_dict
        except Exception as e:
            logger.error(f"Fallback parsing also failed: {e}")

        # Step 7: Give up
        logger.warning("Failed to fix or parse JSON. Returning None.")
        return None



    def response_cleaning(self,response):
       
        if isinstance(response, (list, tuple)) and len(response) > 0:
            response = str(response[0]).strip()

        if not isinstance(response, str):
            return {}

        response = response.replace('```json\n', '').replace('```', '').strip()

        try:
            cleaned_dict = json.loads(response)  # Try parsing normally
            logger.info("JSON parsed successfully without fixes.")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error during cleaning the model result: {e}")

            # Attempt to fix and parse again
            fixed_json = self.clean_and_fix_json(response)

            if fixed_json:
                logger.info(f"JSON fixed and parsed successfully after cleanup - {fixed_json}")
                cleaned_dict = fixed_json
            else:
                logger.warning("JSON could not be fixed. Returning empty dictionary.")
                return {}

        flat_dict = {}

        def flatten(d, parent_key=""):
            """Recursively flattens nested dictionaries and lists of dictionaries."""
            for k, v in d.items():
                new_key = f"{parent_key}{k}" if parent_key else k
                if isinstance(v, dict):
                    flatten(v, new_key + "_")  # Flatten nested dictionary
                elif isinstance(v, list):
                    if all(isinstance(item, dict) for item in v):  # If list contains dictionaries
                        for index, item in enumerate(v):
                            flatten(item, f"{new_key}{index}_")  # Flatten each dict with index
                    elif all(isinstance(item, (str, int, float)) for item in v):
                        flat_dict[new_key] = ', '.join(map(str, v))
                    else:
                        # Mixed-type list fallback
                        flat_dict[new_key] = ', '.join([str(item) for item in v])                  
                else:
                    flat_dict[new_key] = v  # Store key-value pairs

        flatten(cleaned_dict)  # Call flatten function
        return flat_dict  # Return cleaned and flattened dictionary
    
    def fuzzy_match(self, key, flattened_entities, threshold):
        
        best_match = None
        best_score = 0
        for entity_key, entity_value in flattened_entities.items():
            score = fuzz.ratio(key, entity_key.lower())
            if score > best_score and score >= threshold:
                best_match = entity_value
                best_score = score
        return best_match, best_score
    
    def match_actual_entities(self, entities,customer_type):
        results = []
        logger.info("Starting match_actual_entities")

        if not entities:
            logger.warning("No entities provided for matching.")
            return results

        flattened_entities = {}
        for section, section_data in entities.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    flattened_entities[key.lower()] = value 
            elif isinstance(section_data, str):
                flattened_entities[section.lower()] = section_data

        for entity in self.template_entities:
            entity_customer_type = entity.get('entity_key_customer_type', '').strip().lower()
            entity_name = entity.get('entity_name', '').strip().lower()


            if customer_type == "individual":
                if entity_customer_type not in ("individual", "both"):
                    continue
           
            else:
                logger.warning(f"Unrecognized customer type: {customer_type}")
                continue
            entity_name = entity.get('entity_name', '').lower()

            if not entity_name:
                logger.warning(f"Skipping entity with missing entity_name: {entity}")
                continue

            value = flattened_entities.get(entity_name)
            if value:
                logger.info(f" Direct match found for '{entity_name}': {value}")
            else:
                # Try fuzzy match
                fuzzy_value, score = self.fuzzy_match(entity_name, flattened_entities, threshold=70)
                if fuzzy_value:
                    logger.info(f" Fuzzy match for '{entity_name}': Score={score}, Value='{fuzzy_value}'")
                    value = fuzzy_value
                else:
                    logger.info(f" No match found for '{entity_name}'")

            if value:
                entity["entity_value"] = value
                entity["model"] = self.model
                results.append(entity)

        logger.info(f" Total matched entities: {len(results)}")
        return results
