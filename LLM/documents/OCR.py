import os
import os
import cv2
from io import BytesIO
from PIL import Image
from utils.log import logger
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import pandas as pd
import time
from deskew import determine_skew
from dotenv import load_dotenv
load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"
ocrEndpoint =  os.getenv("ocrEndpoint")
subscriptionKey = os.getenv("subscriptionKey")


computervision_client = ComputerVisionClient(ocrEndpoint, CognitiveServicesCredentials(subscriptionKey))

import cv2, imutils, time, os, shutil
import numpy as np



def call_azure_ocr(IMAGE_PATH):
    img = IMAGE_PATH.convert("RGBA")
    data = IMAGE_PATH.getdata()
    extracted_text = azure_ocr(img)
    extracted_text = post_processing(extracted_text)
    # logger.info(f"extracted_text Line 35 :: {extracted_text}")
    return extracted_text


def recreate_folder(path):
    if os.path.exists(path) and os.path.isdir(path):
        # os.rmdir(path)  # This removes the folder if it is empty
        shutil.rmtree(path)
    elif os.path.exists(path):
        return

    os.mkdir(path)

def azure_ocr(image):
    image = imutils.resize(np.array(image), width=2000)
    
    recreate_folder("images")

    cv2.imwrite("images/buffer.jpg", image)
    computervision_client = ComputerVisionClient(ocrEndpoint, CognitiveServicesCredentials(subscriptionKey))

    with open('images/buffer.jpg', 'rb') as image_stream:
        read_response = computervision_client.read_in_stream(image_stream, raw=True)

    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    value = []
    words = []
    line_number = 0
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                line_number += 1
                value.append({'line':line.text, 'bbox':  line.bounding_box})
                for word in line.words:
                    words.append({'word':word.text, 'bbox':  word.bounding_box, 'line_number': line_number})

        #Handle Blank Page
        if not value and not words:  # No text detected
            sample_bbox =[0, 0, 100, 0, 100, 100, 0, 100]
            value.append({'line': 'BLANK_PAGE', 'bbox': sample_bbox})  
            words.append({'word': 'BLANK_WORD0099', 'bbox': sample_bbox, 'line_number': 1}) 
            logger.info(f"This Page is BLANK PAGE.")


        return {'line': value, 'words':words}


def get_corrdinate(x):
    x1 = sum(x[::2])/4
    y1 = sum(x[1::2])/4
    return (x1,y1)


def skew_correction(image):
    angle = determine_skew(image)
    if abs(angle) > 0.5 and int(abs(angle))<45 :
        image = imutils.rotate_bound(image, -determine_skew(image))
        skew_correction(image)
    return image


# function for finding average
def Average(lst):
    # average function
    avg = np.average(lst)
    return(avg)


def get_threshold(words):
    data = pd.DataFrame(words)
    x_ = data.groupby(by='line_number')
    overall_space_diff = []
    for _, each in list(x_):
        for i in range(1, each.shape[0]):
            prev_word_end = each.iloc[i-1]['bbox'][2]

            curr_word_start = each.iloc[i]['bbox'][0]

            # Calculate space difference between current word and previous word
            space_diff = abs(curr_word_start - prev_word_end)
            overall_space_diff.append(space_diff)
    # return Average(overall_space_diff)
    return 15


def post_processing(data):
    line_info = data['line']
    words = data['words']
    space_difference_threshold = get_threshold(words)
    data = pd.DataFrame(line_info)
    data['mean'] =  data['bbox'].apply(lambda x: get_corrdinate(x)  )
    data['line_number'] = -1
    base = 0
    line = 0
    min_x = 1000
    variations = 20
    considered_index = []
    for index, row in data.iterrows():
        x_coordinates = row['bbox']
        x_coordinates = x_coordinates[::2]
        min_x = min(min(x_coordinates), min_x)
        if index in considered_index:
                continue
        line = line + 1
        data.at[index, 'line_number'] = line
        y = row['mean'][1]
        for index2, row2 in data.iterrows():
            if index2 in considered_index:
                continue
            if index >= index2:
                continue
            y2 = row2['mean'][1]
            if abs(y - y2) < variations:
                # print('here')
                # print(row)
                considered_index.append(index2)
                data.at[index2, 'line_number'] = line
    data['x'] = data['mean'].apply(lambda x: x[0])
    data=data.sort_values(by = ['line_number', 'x'], ascending = [True, True], na_position = 'first')
    x_ = data.groupby(by='line_number')
    text = ''
    # space_difference_threshold = 20  #
    for index, each in list(x_):
        temp_text = ''
        for i in range(0, each.shape[0]):
            if i ==0:
                prev_word_end = min_x
            else:
                prev_word_end = each.iloc[i-1]['bbox'][2]

            curr_word_start = each.iloc[i]['bbox'][0]

            # Calculate space difference between current word and previous word
            space_diff = curr_word_start - prev_word_end

            # If the space difference is large, add more space (this threshold can be adjusted)
            if space_diff > space_difference_threshold:
                # temp_text += '|'  # Add spaces proportional to the difference
                temp_text += ' ' * int(space_diff / space_difference_threshold)  # Add spaces proportional to the difference
            temp_text += each.iloc[i]['line']

        text = text + temp_text + "\n"

    # file1 = open("___text.txt","w",encoding="utf-8")
    # file1.write(text)
    # file1.close()
    return text

