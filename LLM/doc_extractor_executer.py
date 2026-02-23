from documents.TIFDocument import TIFFDocument 
from documents.PDFDocument import PDFDocument 
from documents.IMGDocument import IMGDocument
import io
from classification import Classify
from extraction import Extraction
from utils.log import logger
from extraction.aimodel.aimodel_extraction import AIMODELExtractor
from classification.aimodel.aimodel_classification import AIMODELClassifier
from utils.payload_processing import get_entities
import json
from dotenv import load_dotenv
load_dotenv()
import os

class DocExtractor:
    def __init__(self, file):
        """Initialize DocExtractor with a file in bytes format and attempt to create the appropriate document object."""
        self.document = None
        file_bytes=file.read()
        file_extension = file.filename.rsplit('.', 1)[-1].lower()
        
        if file_extension=="pdf":
            try:
                self.document = PDFDocument(file_bytes) 
            except Exception as e_pdf:
                logger.error(f"PDF processing failed: {e_pdf}")
        elif file_extension in ['tiff', 'tif']:
            try:
                self.document = TIFFDocument(file_bytes)
            except Exception as e_tiff:
                logger.error(f"TIFF processing failed: {e_tiff}")
        elif file_extension in ["png","jpeg","jpg"]:
            try:
                self.document=IMGDocument(file_bytes)
            except Exception as imgdoc:
                logger.error(f"IMG processing failed: {imgdoc}")
        else:
            logger.error(f"Unsupported file format: {file_extension}")

    def get_results(self):
        """Retrieve the classification and extraction results."""
        return {
            "classification_results": self.classification_results,
            "extraction_results": self.extraction_results
        }

    def get_document(self):
        """Retrieve the initialized document object."""
        return self.document
    
    def get_classification_extraction(self, formatted_data_for_prompt):
        global template_classifier

        classification_model_company = os.getenv("CLASSIFICATION_MODEL_COMPANY")
        classifier_model = AIMODELClassifier(self.document, classification_model_company)
        classifier_model.classify_pages(formatted_data_for_prompt)
        self.document.unify_classification(formatted_data_for_prompt) 


        extraction_model_company=os.getenv("EXTRACTION_MODEL_COMPANY")
        ner_model = AIMODELExtractor(self.document,extraction_model_company)  
        ner_model.extract_pages(formatted_data_for_prompt)
        self.document.unify_extraction()




def start_doc_extractor(file, template_data):
    global template_classifier
    if file:
        if template_data:
            if extract_templates(template_data, False):
                logger.info("UI Templates extracted successfully")

        entitie_data, _ = get_entities(template_data)
        formatted_data_for_prompt = entitie_data['data']

        doc_extractor = DocExtractor(file)
        doc_extractor.get_classification_extraction(formatted_data_for_prompt)
        
        extracted_page_details = doc_extractor.document.get_page_details()
        
        return extracted_page_details



def extract_templates( template_data, init_templates= True):
    global template_classifier
    try:
        if template_data:
            _ , template_data = get_entities(template_data)
            # if template_data:
                # template_classifier = tfIDFTemplateClassifier(template_data, init_templates)
            return True
    except Exception as error:
            logger.error(f"issue with the document {error}")