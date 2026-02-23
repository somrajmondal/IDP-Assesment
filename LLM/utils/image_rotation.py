import time
import cv2
import os
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import shutil
from PIL import Image
import imutils
from dotenv import load_dotenv

load_dotenv()

ocrEndpoint = os.getenv("ocrEndpoint")
subscriptionKey = os.getenv("subscriptionKey")

rotation_folder = "utils/images_rotation"

def recreate_folder(path):
    """Delete and recreate a folder."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def get_orientation_angle(image):
    """Get the orientation angle of an image using Azure OCR."""
    image = imutils.resize(np.array(image), width=2000)
    recreate_folder(rotation_folder)
    
    image_path = os.path.join(rotation_folder, "buffer.jpg")
    cv2.imwrite(image_path, image)

    client = ComputerVisionClient(ocrEndpoint, CognitiveServicesCredentials(subscriptionKey))

    with open(image_path, 'rb') as image_stream:
        ocr_result = client.read_in_stream(image_stream, raw=True)
        operation_location = ocr_result.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower() in ['succeeded', 'failed']:
            break
        time.sleep(1)

    if result.status.lower() == 'succeeded' and result.analyze_result.read_results:
        return result.analyze_result.read_results[0].angle
    return 0  # Default return if no angle is detected

def correct_orientation(image, angle):
    """Rotate the image based on detected angle."""
    if angle == 0:
        return image  # No rotation needed

    if angle < -45:
        angle += 90
    elif angle > 45:
        angle -= 90

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected

def process_and_correct_image(image):
    """Detect orientation and correct image rotation."""
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGR)

    angle = get_orientation_angle(image)
    corrected_image = correct_orientation(image, angle)
    return corrected_image

def call_azure_ocr_IMAGE_Rotation(image):
    """Full pipeline for processing image orientation with Azure OCR."""
    img = image.convert("RGBA")
    corrected_img = process_and_correct_image(img)
    return Image.fromarray(cv2.cvtColor(corrected_img, cv2.COLOR_BGR2RGB))  # Convert back to PIL

def process_image_from_path(file_path):
    """Load, correct, and return an image from a file path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "rb") as file:
            img = Image.open(file)
            img = img.convert("RGBA")  # Ensure it's in a valid format

        corrected_img = call_azure_ocr_IMAGE_Rotation(img)
        return corrected_img
    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")

