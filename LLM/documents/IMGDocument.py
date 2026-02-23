from documents.Document import Document
from PIL import Image
import os
from documents.OCR import call_azure_ocr
from io import BytesIO
from utils.log import logger
from collections import defaultdict
from utils.image_rotation import call_azure_ocr_IMAGE_Rotation
import numpy as np

class IMGDocument(Document):
    def __init__(self, file_bytes):
        try:
            img = Image.open(BytesIO(file_bytes))
            img_format = img.format.upper() if img.format else 'JPEG'  
            img = img.convert("RGB")  
            super().__init__(file_bytes, 1, img_format)

            self.pagewise_images = defaultdict(list)
            self.pagewise_text = defaultdict(list)

            try:
                img = call_azure_ocr_IMAGE_Rotation(img)
            except Exception as e:
                logger.warning(f"Image rotation failed: {e}")

            self.add_image_to_page(1, img)

        except Exception as e:
            raise RuntimeError(f"Error initializing IMGDocument: {e}")




    def perform_ocr(self, page_number, image, do_ocr=False):
        try:
            if do_ocr:
                self.pagewise_text[page_number].append(call_azure_ocr(image))
            elif not image:
                logger.warning(f"Skipping page {page_number} due to missing or invalid image data.")
                self.pagewise_text[page_number].append("")
        except AssertionError as error:
            self.pagewise_text[page_number].append("")  
            logger.warning(f"Skipping page {page_number} due to invalid OCR credential: {error}")
        except Exception as error:
            self.pagewise_text[page_number].append("")  
            logger.warning(f"Skipping page {page_number} due to unexpected OCR error: {error}")
    

    def unify_extraction_id_passport(self):
        for page_number in range(1, self.num_pages + 1):
            page_entities = self.pagewise_entities.get(page_number, [])
            classification = self.pagewise_classification.get(page_number, {}).get("class_name", "")


            if classification in[ "Emirates ID","Passport"]:

                if not page_entities:
                    logger.warning(f"No entities found for page {page_number}")
                    continue

               

                aimodel_data = next(
                    (entity.get("extraction_matched_data", []) 
                    for entity in page_entities 
                    if entity.get("source") == "aimodel" and entity.get("extraction_matched_data")),
                    []
                )

                unified_result = aimodel_data
                if unified_result:
                    self.pagewise_entities[page_number] = unified_result
                    logger.info(f"ID model result saved for page {page_number}")
                else:
                    logger.warning(f"No ID model data found for page {page_number}")
            else:
                continue


    def add_image_to_page(self, page_number, image):
        """Add an image to a specific page."""
        if 1 <= page_number <= self.num_pages:
            self.pagewise_images[page_number].append(image.copy())
            self.perform_ocr(page_number, image, True)
        else:
            raise ValueError("Invalid page number.")

    def get_page_image(self, page_number):
        return self.pagewise_images.get(page_number, None)

    def __str__(self):
        return (super().__str__() + f"\nPagewise Images: {[key for key in self.pagewise_images.keys()]}")

