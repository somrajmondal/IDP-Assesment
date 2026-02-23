import json
from utils.log import logger
import re

def get_templates(data):
    formatted_data = {"message": "Data fetched successfully!", "data": []}

    try:
        for item in data:
            if "templates" in item and isinstance(item["templates"], list) and item["templates"]:
                templates_list = []
                for template in item["templates"]:
                    # Ensure entities exist and are not empty before accessing index 0
                    entity_template = template.get("entities", [{}])[0].get("template", {})

                    formatted_template = {
                        "template_id": template.get("template_id"),
                        "file": entity_template.get("file"),
                        "description": entity_template.get("description"),
                        "describe_document": entity_template.get("describe_document"),
                        "keywords": entity_template.get("keywords"),
                        "is_active": entity_template.get("is_active"),
                        "is_complete": entity_template.get("is_complete")
                    }
                    templates_list.append(formatted_template)

                formatted_item = {
                    "id": item.get("id"),
                    "document_name": item.get("document_name"),
                    "customer_type": item.get("customer_rp_flag", {}).get("customer_type", ""),
                    "document_backend_key": item.get("document_backend_key"),
                    "features": item.get("features"),
                    "templates": templates_list
                }
                formatted_data["data"].append(formatted_item)

    except Exception as e:
        logger.error(f"Error occurred while processing the data: {e}")
        formatted_data["message"] = f"Error occurred: {str(e)}"
    
    return formatted_data


def get_entities(data):
    formatted_data = {"data": []}

    try:
        for item in data:
            formatted_item = {
                "id": item.get("id"),
                # "entity_type": "individual",
                "document_name": item.get("document_name"),
                "customer_type": item.get("customer_rp_flag", {}).get("customer_type", ""),
                "t24_rp_flag": item.get("customer_rp_flag", {}).get("rp_applicable_flag", ""),
                "document_backend_key": item.get("document_backend_key"),
                "features": item.get("features", "Document contains details about the entity."),
                "related_entities": []
            }

            for template in item.get("templates", []):
                for entity in template.get("entities", []):
                    formatted_item['description'] =  entity.get("template").get('describe_document', "")
                    formatted_item['description_for_non_individual'] =  entity.get("template").get('description_for_non_individual', "")
                    formatted_item["related_entities"].append({
                        "entity_name": entity.get("entity_name"),
                        "entity_context": entity.get("entity_context", "{}"),
                        "entity_data_type": entity.get("entity_data_type"),
                        "entity_key_customer_type":entity.get("entity_key_customer_type"),
                        "entity_key_rp_type":entity.get("entity_key_rp_type"),
                        "backend_entity_key": entity.get("backend_entity_key"),
                        "entity_description": entity.get("entity_description")
                    })

            formatted_data["data"].append(formatted_item)

    except Exception as e:
        logger.error(f"Error occurred while processing the entities: {e}")
        formatted_data["message"] = f"Error occurred: {str(e)}"

    return formatted_data, get_templates(data)

def clean_raw_data(raw_data):
    raw_data = raw_data.replace("'", '"')
    # Handle datetime.date(x, y, z) by replacing with "YYYY-MM-DD" format
    raw_data = re.sub(r'datetime\.date\((\d{4}), (\d{1,2}), (\d{1,2})\)', r'"\1-\2-\3"', raw_data)

    # Handle Python None by replacing it with JSON null
    raw_data = raw_data.replace("None", "null")
    raw_data = raw_data.replace("False", "false")  
    raw_data = raw_data.replace("True", "true") 
    return raw_data