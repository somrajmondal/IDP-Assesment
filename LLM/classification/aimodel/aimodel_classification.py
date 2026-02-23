from classification.Classify import Classify
from utils.llm import openai_client, gemini_model
from utils.log import logger
from utils.prompt import (
    aimodel_classify_promt_level1,
 
)
import os


class AIMODELClassifier(Classify):
    def __init__(self, document, model):
        super().__init__(document, model, None)
        self.model = model  

    def define_prompt(self, templates, level=1):
        customer_type = {
            str(template.get("customer_type", "")).lower()
            for template in templates
        }

        is_individual = "individual" in customer_type

        if is_individual:
            if level == 1:
                SYSTEMP_PROMT = aimodel_classify_promt_level1()
                template_info = {
                    template["document_name"]: template.get("description", "")
                    for template in templates
                }
                formatted_string = "\n".join(
                    [
                        f"Class: {class_name}\n Definition:\n{class_description}\n"
                        for class_name, class_description in template_info.items()
                    ]
                )
                class_label = "\n".join(
                    [f"{class_name}, " for class_name in template_info]
                )
                self.class_name = list(template_info.keys())
                SYSTEMP_PROMT = SYSTEMP_PROMT.format(
                    template_definition=formatted_string,
                    class_name=class_label
                )
                logger.info("Classification:: STEP 1: Classification Prompt formatted and sent to model")
                return SYSTEMP_PROMT

  
        
    def prediction_GEMINI(self, messages, level):
        try:
            logger.info("Classification:: Sending request to Gemini model")
            text_parts = []
            for m in messages:
                if m["role"] == "user":
                    for content in m.get("content", []):
                        if content["type"] == "text":
                            text_parts.append(str(content.get("text") or ""))
                elif m["role"] == "system":
                    text_parts.append(f"System Instruction: {str(m.get('content') or '')}")

            prompt = "\n\n".join(text_parts)

            response = gemini_model.generate_content(prompt)
            output_text = response.text

            logger.info(f"Classification:: Gemini result:: {output_text}")
            return self.response_cleaning(output_text, level=level)

        except Exception as e:
            logger.error(f"Classification:: Gemini API call failed: {e}")
            return []


    def prediction_OPENAI(self, messages, level):
        try:
            logger.info("Classification:: Sending request to OpenAI model")
            response = openai_client.chat.completions.create(
                model=os.getenv("OPENAI_CLASSIFICATION_MODEL"),
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )
            output_text = response.choices[0].message.content
            logger.info(f"Classification:: STEP 2: Classification result received from OpenAI  {output_text}")
            classification_result = self.response_cleaning(output_text, level=level)
            return classification_result

        except Exception as e:
            logger.error(f"Classification:: OpenAI API call failed: {e}")
            return []

    def classify_pages(self, templates, level=None):  
        level = level or 1
        model = self.model  

        if self.document is not None:
            for page_number, image in self.document.pagewise_images.items():
                customer_type = {
                    str(template.get("customer_type", "")).lower()
                    for template in templates
                }
                is_individual = "individual" in customer_type
                self.document.page_customer_type[page_number] = (
                    "individual" if is_individual else "non-individual"
                )

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
                            "You are a document classification assistant. Use the user input and classification prompt "
                            "to classify the document. Provide a single class name from the list of classes provided in the user prompt."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"OCR Text:\n{ocr_text_str.strip()}"},
                            {"type": "text", "text": self.define_prompt(templates, level=level)},
                        ],
                    },
                ]

                try:
                    if model == "openai":
                        classification_result = self.prediction_OPENAI(messages, level)
                    elif model == "gemini":
                        classification_result = self.prediction_GEMINI(messages, level)
                    else:
                        logger.error(f"Classification:: Unsupported model type: {model}")
                        continue

                    self.document.classify_page(page_number, classification_result)

                except Exception as e:
                    logger.error(f"Classification:: Error classifying page {page_number}: {e}")
