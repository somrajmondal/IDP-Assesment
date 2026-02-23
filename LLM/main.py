import utils.load_env
from utils.log import setup_logger, logger
logger = setup_logger()
from quart import Quart, request, jsonify
from quart_cors import cors
import json
from doc_extractor_executer import start_doc_extractor
from dotenv import load_dotenv
load_dotenv()
import os

app = Quart(__name__)
app = cors(app, allow_origin="*")  

logger.info("--------------------------------------------------------------------------------------")
logger.info("Server started.")

     
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

@app.route('/up_doc', methods=['POST','GET'])
async def process_docdata():
    if request.method == 'GET':
        
        return jsonify({"message": "This is GET"})

    if request.method == "POST":
        form_data = await request.form  

        json_data = form_data.get('json') 
      

        force_individual =True

        customer_rp_flag = {
        "customer_type": "Individual" if force_individual else "Non-Individual",
        "rp_applicable_flag": "Yes" if force_individual else "No"
        }

        if json_data:
            json_data = json.loads(json_data)  
            if type(json_data)  == list:
                document_data = json_data
            else:
                document_data = json_data.get("data", [])
            for item in document_data:
                item["customer_rp_flag"] = customer_rp_flag

            # document_data=json_data
        else:
            document_data = []

        logger.info(f"json_data: {document_data}")


        files = await request.files 
        file_list = files.getlist('files') 
 
        logger.info(f"file_list: {file_list}")
        for file in file_list:
            if file.filename == '':
                return jsonify({"error": "One or more files have no filename"}), 400
            
            ALLOWED_EXTENSIONS={"tiff", "tif", "pdf","png","jpeg","jpg"} 
            file_extension = file.filename.rsplit('.', 1)[-1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                return jsonify({"error": f"Invalid file type: .{file_extension}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
                
            extracted_data = start_doc_extractor(file, document_data)
            logger.info(f"file name {file.filename}")
            logger.info(json.dumps(extracted_data, indent=3))
            logger.info("request complete")

    return jsonify({"extraction_status":"completed","extracted_data":extracted_data})



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002)
