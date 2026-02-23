from dateutil import parser
import re
from utils.log import logger
from deep_translator import GoogleTranslator

class Formatter:
    @staticmethod
    def format_date(raw_date_string):
        try:
            # If the string starts with 4 digits,  (YYYY-MM-DD)
            if re.match(r'^\d{4}', raw_date_string):
                parsed_date = parser.parse(raw_date_string)
            else:
                parsed_date = parser.parse(raw_date_string, dayfirst=True)
            return parsed_date.strftime('%Y-%m-%d')
        except Exception:
            return  {"raw_output": raw_date_string, "manual_check": True}  
    @staticmethod    
    def format_trade_license_number(license_string):
        try:
            cleaned= re.sub(r'[^a-zA-Z0-9]','',str(license_string))
            return cleaned
        except Exception:
            return license_string


    @staticmethod
    def format_idnumber(id_string):
        try:
            cleaned_id = re.sub(r'[^a-zA-Z0-9]', '', str(id_string))
            return cleaned_id[-15:]
        except Exception:
            return id_string 
        
    @staticmethod
    def format_passportno(number_string):
        try:
            number_string = number_string.replace(" ", "")
            
            if len(number_string) >= 9:
                number_string = number_string[:9]
                return number_string
            elif len(number_string) < 9:
                return {"raw_output": number_string, "manual_check": True}
        except Exception:
            return {"raw_output": number_string, "manual_check": True}
        
   
        
    @staticmethod
    def cleaning_for_UI(raw_json):
        include_pages = {}
        found_emirates_id = False
       
        found_passport = False
        selected_categories = set()  # Track selected categories for Account Opening Forms

        entity_mappings = {
            "emirates id": {"emirates_id_number", "eid_expiry_date", "eid_issuance_date", "country_of_residency"},
            "passport": {"place_of_birth", 
                    "customer_name_passport", "date_of_birth", "passport_expiry_date", 
                     "passport_number",}
        }

        class_thresholds = {
            "emirates id": 0.75,
            "passport": 0.50
        }


        excluded_pages = {}  # Store excluded pages and entities
   
      

        for page, data in raw_json.items():
            extracted_class = data["classification"]["class_name"].lower()
            if "extraction" not in data:
                continue

      
            if extracted_class == "emirates id":
                if found_emirates_id:
                    excluded_pages[page] = data
                    include_pages[page] = {
                        "classification": data["classification"],
                        "status":"duplicate_class",
                        "extraction": []
                    }
                    continue
                for item in data.get("extraction", []):
                    if item.get("backend_entity_key") == "country_of_residency":
                        item["entity_value"] = "AE"

                    if item.get("backend_entity_key") == "emirates_id_number":
                        id_number = item.get("entity_value")

                        if len(id_number) > 15:
                            logger.info(f"Before Formatting: {id_number}")
                            VALID_NUMBER = Formatter.format_idnumber(id_number)
                            logger.info(f"After Formatting: {VALID_NUMBER}")
                            item["entity_value"] = VALID_NUMBER

                            include_pages[page] = {
                                "classification": data["classification"],
                                "extraction": [i for i in data["extraction"] ] }
                            continue

                        elif len(id_number) == 9:
                            # Filter out 'emirates_id_number' from extraction
                            filtered_extraction = [
                                i for i in data["extraction"] 
                                if i.get("backend_entity_key") != "emirates_id_number"
                            ]
                            include_pages[page] = {
                                "classification": data["classification"],
                                "extraction": filtered_extraction
                            }
                            continue

                        # Optional condition to exclude other cases
                        # e.g. missing hyphen or invalid format
                        excluded_pages[page] = {
                            "classification": data["classification"],
                            "status": "this is Visa card",
                            "extraction": []
                        }
            


            elif extracted_class == "passport":
                if found_passport:
                    excluded_pages[page] = data
                    include_pages[page] = {
                        "classification": data["classification"],
                        "status":"duplicate_class",
                        "extraction": []
                    }
                    continue
                required_entities = entity_mappings.get(extracted_class)
                threshold = class_thresholds.get(extracted_class, 0.50)
                entity_names = {item["backend_entity_key"] for item in data["extraction"]}
                matching_entities = entity_names.intersection(required_entities)
                if len(matching_entities) >=  len(required_entities) * threshold:
                    include_pages[page] = {
                        "classification": data["classification"],
                        "extraction": [item for item in data["extraction"]
                                    if item["backend_entity_key"] in matching_entities]
                    }
                else:
                    excluded_pages[page] = data
                    include_pages[page] = {
                        "classification": data["classification"],
                        "extraction": []
                    }

            else:
                include_pages[page] = data  

        return include_pages, excluded_pages

if __name__ == "__main__":
    d1 = "2020/7/3"
    d2 = "03/07/2020"

    