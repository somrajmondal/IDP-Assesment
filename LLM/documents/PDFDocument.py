from documents.Document import Document
from pdf2image import convert_from_bytes
from documents.OCR import call_azure_ocr
from utils.log import logger
from collections import defaultdict
from utils.image_rotation import call_azure_ocr_IMAGE_Rotation
import numpy as np

class PDFDocument(Document):
    def __init__(self, filename):
        """Initialize the PDFDocument, extract images, and store pagewise data."""
        try:
            images = convert_from_bytes(filename)
            self.num_pages = len(images)
            super().__init__(filename, self.num_pages, "PDF")
            self.pagewise_images =defaultdict(list)
            self.pagewise_text = defaultdict(list)
            for page_number, image in enumerate(images, start=1):
                try:
                    image = call_azure_ocr_IMAGE_Rotation(image)
                    self.add_image_to_page(page_number, image)
                except Exception as e:
                    self.add_image_to_page(page_number, image)

        except Exception as e:
            raise RuntimeError(f"Error initializing PDFDocument and extracting images: {e}")

    def perform_ocr(self, page_number, image, do_ocr = False):
        try:
            if do_ocr:
                ocr_result = call_azure_ocr(image)
                self.pagewise_text[page_number].append(ocr_result)
        except Exception as error:
            raise AssertionError(f"Invalid OCR credential, {error}")

    def unify_extraction_id_passport(self):
        for page_number in range(1, self.num_pages):
            page_entities = self.pagewise_entities.get(page_number, [])
            classification = self.pagewise_classification.get(page_number, {}).get("class_name", "")

            if classification in[ "Emirates ID","Passport"]:

                if not page_entities:
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
            self.pagewise_images[page_number].append(image)
            self.perform_ocr(page_number, image, True)
        else:
            raise ValueError("Invalid page number.")

    def get_page_image(self, page_number):
        """Retrieve the image of a specific page."""
        return self.pagewise_images.get(page_number, None)

    def __str__(self):
        """Return a string representation of the PDF document."""
        return (super().__str__() + f"\nPagewise Images: {[key for key in self.pagewise_images.keys()]}")
