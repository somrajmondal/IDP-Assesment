from collections import defaultdict
from utils.validation import Formatter
from utils.log import logger
from fuzzywuzzy import fuzz
import json

class Document:
    def __init__(self):
        "Initial "

    def __init__(self, filename=None, num_pages=None, doc_type=None):
        """Initialize the Document with filename, number of pages, and document type."""
        self.filename = filename
        self.num_pages = num_pages
        self.doc_type = doc_type
        self.pagewise_classification = defaultdict(list)  
        self.pagewise_entities =  {}  
        self.pagewise_text = defaultdict(list)
        self.page_customer_type = {} 

    def classify_page(self, page_number, classification, append= True):
        """Classify a specific page with the given classification."""
        if 1 <= page_number <= self.num_pages and append:
            self.pagewise_classification[page_number].append(classification.copy())
        elif not append:
            self.pagewise_classification[page_number] = []
            self.pagewise_classification[page_number].append(classification.copy())
        else:
            raise ValueError("Invalid page number.")

    def add_entities_to_page(self, page_number, entities):
        """Add entities to a specific page."""
        if 1 <= page_number <= self.num_pages:
            formatted_entities = self.formatted_entities(entities)
            if page_number not in self.pagewise_entities:
                self.pagewise_entities[page_number] = []
            self.pagewise_entities[page_number].append(formatted_entities.copy())
        else:
            raise ValueError("Invalid page number.")
        
    def formatted_entities(self, entities):
        formatted_entities = []
        for single_item in entities:
            backend_key = single_item.get("backend_entity_key", "")
            entity_value = single_item.get("entity_value", "")

            formatted_item = single_item.copy()
            try:
                if backend_key == "emirates_id_number":
                    pass

                elif backend_key in {"date_of_birth", "eid_expiry_date", "eid_issuance_date",
                                    "passport_expiry_date", "passport_issuance_date",
                                   }:
                    
                    formatted_item["entity_value"] = Formatter.format_date(entity_value)

                elif backend_key in {"passport_number"}:
                    formatted_item["entity_value"]=Formatter.format_passportno(entity_value)
              
            except Exception as e:
                logger.error(f"Error formatting entity '{backend_key}': {e}")
            formatted_entities.append(formatted_item)
        return formatted_entities


    def get_page_classification(self):
        """Retrieve the classification of a specific page."""
        return self.pagewise_classification
    def get_ocr_text(self, page_number=None):
        
            if page_number:
                if 1 <= page_number <= self.num_pages:
                    return self.pagewise_text.get(page_number, [])
                else:
                    raise ValueError("Invalid page number.")
            return dict(self.pagewise_text)
    def get_page_details(self):
        results = defaultdict(dict)
        for page_number in self.pagewise_classification:
            results[page_number].update({"classification":self.pagewise_classification[page_number].copy()})
        for page_number in self.pagewise_entities:
            results[page_number].update({"extraction":self.pagewise_entities[page_number].copy()})
            
        include_pages,excluded_pages= Formatter.cleaning_for_UI(results)
        logger.info(f"RAW RESULT:\n{json.dumps(results, indent=3)}")
        logger.info(f"EXCLUDE PAGES RESULT:\n{json.dumps(excluded_pages, indent=3)}")
        return include_pages 

    def get_page_entities(self):
        
        """Retrieve the entities of a specific page."""
        return self.pagewise_entities

    def unify_classification(self, templates):
        for page_number in range(1, self.num_pages + 1):
            classes = self.pagewise_classification[page_number]
            if len(classes) == 1:
                self.pagewise_classification[page_number] = classes[0].copy()

                logger.info(f"Classification:: STEP 4: Only one class found from openai, result returned -- {classes[0].copy()}")
            elif len(classes) > 1:
                if classes[0]['class_name'] == classes[1]['class_name']:
                    self.pagewise_classification[page_number] = classes[0].copy()
                    logger.info(f"Classification:: STEP 4: Overall classes, result returned -- {classes[0].copy()}")
                else:
                    classes[0].update({
                        "score": 0.5,
                        "manual_check": True,
                        "other_prediction": classes[1].copy()
                    })
                    self.pagewise_classification[page_number] = classes[0].copy()
                    logger.info(f"Classification:: STEP 4: Conflicting classes, result returned -- {classes[0].copy()}")

    def unify_extraction(self):
        considered_entities = []
        threshold=70
        for page_number in range(1, self.num_pages+1):
            entities =  self.pagewise_entities[page_number]

            aimodel_data = entities[0] if len(entities) > 0 else []
            numind_data = entities[1] if len(entities) > 1 else None

            if numind_data is None:
                for aimodel_v in aimodel_data:
                    aimodel_v['checked'] = False
                self.pagewise_entities[page_number] = aimodel_data.copy()
                continue

            for aimodel_v in aimodel_data:
                matched = False
                aimodel_v['checked'] = False

                for numin_v in numind_data:
                    if aimodel_v['entity_name'] == numin_v['entity_name']:
                        matched = True
                        considered_entities.append(aimodel_v['entity_name'])
                        similarity_score = fuzz.ratio(
                            str(aimodel_v['entity_value']).lower(), 
                            str(numin_v['entity_value']).lower()
                        )
                        if similarity_score >= threshold:
                            aimodel_v['checked'] = True
            
            for numin_v in numind_data:
                if numin_v['entity_name'] not in considered_entities:
                    considered_entities.append(numin_v['entity_name'])
                    numin_v['checked'] = False
                    numin_v['model'] = 'nu-mind'
                    aimodel_data.append(numin_v)
            self.pagewise_entities[page_number] = aimodel_data.copy()

    def __str__(self):
        """Return a string representation of the document."""
        return (f"Filename: {self.filename}\n"
                f"Number of Pages: {self.num_pages}\n"
                f"Document Type: {self.doc_type}\n"
                f"Pagewise Classification: {self.pagewise_classification}\n"
                f"Pagewise Entities: {self.pagewise_entities}")