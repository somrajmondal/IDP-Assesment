import re
from utils.log import logger

class Classify:
    def __init__(self, document, classifier_model,extra_param=None):
        """Initialize the Classify class with a Document object and a classification model."""
        self.document = document
        self.classifier_model = classifier_model
        self.class_name = []

    def classify_pages(self):
        """Classify each page of the document into specific categories."""
        for page_number in range(1, self.document.num_pages + 1):
            page_content = f"Content of page {page_number}"  # Placeholder for actual page content
            classification = self.classifier_model.classify(page_content)
            self.document.classify_page(page_number, classification)
        return {
            "filename": self.document.filename,
            "pagewise_classification": self.document.pagewise_classification
        }
    
    def response_cleaning(self, original_response, level=1):
        # Remove newlines, backticks, and extra spaces
        cleaned_response = original_response.replace("\n", " ").strip("\"',`").strip()

        

        return {
            "class_name": cleaned_response,
            "score": 1,
            "technique": f"{self.classifier_model} - level {level}"
        }




    
