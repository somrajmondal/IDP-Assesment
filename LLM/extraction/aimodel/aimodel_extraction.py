from extraction.Extraction import Extraction
from utils.llm import openai_client,gemini_model
from utils.prompt import  aimodel_extraction_promt1
from utils.log import logger
import os

class AIMODELExtractor(Extraction):
    def __init__(self, document,model):
        super().__init__(document,model)
        self.model = model  

    def define_prompt(self, templates, doc_name):
        doc_template = next(
        (template for template in templates if template['document_name'] == doc_name['class_name']),{})
                                                                                                                                                                                                    
        customer_type = str(doc_template.get('customer_type', '')).lower()

        is_individual = customer_type == 'individual'
        

    
        SYSTEMP_PROMT = aimodel_extraction_promt1()

        formatted_string = ""
        
        self.template_entities = doc_template.get('related_entities', [])

        if is_individual:
            # Case 1: Individual
            filter_entities = [
                            e for e in self.template_entities
                            if e.get("entity_key_customer_type", "").lower() in ["individual","both"]
                        ]
       


    
        # Format the prompt input
        formatted_string = "\n\n".join([
            f'entity_name: "{ent_name}", entity_description: "{ent.get("entity_description", f"This is the **{ent_name}**. Provide the exact value as it appears in the document.")}"'
            for ent in filter_entities
            for ent_name in [ent["entity_name"]]
        ])


        SYSTEMP_PROMT = SYSTEMP_PROMT.replace("entities_list", formatted_string)

        logger.info("Extraction:: STEP1: Extraction Entity and Description has sent to Model Prompt")

        return SYSTEMP_PROMT



    def zoom_image(self, image):
        from PIL import Image

        # Define the zoom factor
        zoom_factor = 6.0

        # Compute new dimensions
        width, height = image.size
        new_width = int(width * zoom_factor)
        new_height = int(height * zoom_factor)

        # Resize the image (using a high-quality resampling)
        zoomed_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return zoomed_image

    def prediction_GEMINI(self, messages):
        try:
            logger.info(f"Extraction:: Sending request to Gemini model")

            text_parts = []
            for m in messages:
                if m["role"] == "user":
                    for content in m["content"]:
                        if content["type"] == "text":
                            text_parts.append(content["text"])
                elif m["role"] == "system":
                    text_parts.append(f"System Instruction: {m['content']}")

            prompt = "\n\n".join(text_parts)

            response = gemini_model.generate_content(prompt)
            output_text = response.text
            return output_text

        except Exception as e:
            logger.error(f"Gemini Extraction Error: {e}")
            return "{}"


    def prediction_OPENAI(self, messages):
        try:
            logger.info(f"Extraction:: Sending request to OpenAI")

            response = openai_client.chat.completions.create(
                model=os.getenv("OPENAI_EXTRACTION_MODEL"),
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI Extraction Error: {e}")
            return "{}"

    def extract_pages(self, templates, doc_name=1):
        for page_number, image in self.document.pagewise_images.items():

            ocr_text = self.document.pagewise_text.get(page_number, [])
            ocr_text_str = ""
            if ocr_text:
                if isinstance(ocr_text[0], dict) and "text" in ocr_text[0]:
                    ocr_text_str = ocr_text[0]["text"]
                elif isinstance(ocr_text[0], str):
                    ocr_text_str = ocr_text[0]

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an intelligent document parsing assistant. Your job is to extract structured information "
                        "from OCR-scanned text into a valid JSON object from the given entity list in the user prompt."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"OCR Text:\n{ocr_text_str.strip()}"},
                        {"type": "text", "text": self.define_prompt(templates, self.document.pagewise_classification.get(page_number))},
                    ],
                }
            ]

            if self.model == "openai":
                output_text = self.prediction_OPENAI(messages)
            elif self.model == "gemini":
                output_text = self.prediction_GEMINI(messages)
            else:
                logger.error(f"Extraction:: Unsupported model type: {self.model}")
                continue

            logger.info(f"Extraction:: STEP 2: Extraction result received from {self.model.upper()} model {output_text}")

            try:
                extracted_data = self.response_cleaning(output_text)
                customer_type = self.document.page_customer_type.get(page_number, None)
                matched_entities = self.match_actual_entities(extracted_data.copy(), customer_type)

                logger.info(f" Extraction :: {customer_type} Value - page number {page_number}\n{extracted_data}")
                self.document.add_entities_to_page(page_number, matched_entities)
                logger.info(f"Extraction:: STEP3: Page Number {page_number} Extracted result has cleaned")

            except Exception as e:
                logger.error(f"Error parsing extraction results for page {page_number}: {e}")
