import json
import time
import requests
from config import conf
from common.log import logger
import os
from PIL import Image

class CozeUploader:
    def __init__(self):
        pass

    def upload_file(self, session_id: str, file_path: str):
        logger.info(f"[Coze Wrapper] upload_file enter")
        return self.start_upload(session_id, file_path)

    def start_upload(self, session_id, file_path):
        url = f"{self.base_url()}/files/upload"

        #file_path = os.path.abspath(file_path)
        jpg_file_path = os.path.splitext(file_path)[0] + '.jpg'
        #打开PNG文件
        with Image.open(file_path) as img:
            # 转换图像格式为JPG
            img.convert('RGB').save(jpg_file_path, 'JPEG')
        headers = self.headers()
        with open(jpg_file_path, 'rb') as file:
            logger.info(f"[Coze Wrapper] start_upload file={file}")
            response = requests.post(url, headers=headers, files={'file': file})

        response_json = response.json()
        logger.info(f"[Coze Wrapper] start_upload response , response={response_json}")
        if response.status_code == 200:
            if response_json.get("code") == 0:
                data = response_json.get("data")
                file_id = data.get('id')
                logger.info(f"[Coze Wrapper] start_upload response parse, file_id={file_id}")
                return file_id
            else:
                error_msg = response_json.get("msg")
                error_code = response_json.get("code")
                logger.warn(f"[COZE Wrapper] Response Error text={error_msg} status_code={error_code}")
                return None
                
        else:
            error_info = f"[COZE Wrapper] response text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None


    def base_url(self):
        return "https://api.coze.cn/v1"


    def headers(self):
        return {
            'Authorization': f"Bearer {conf().get('coze_api_key', '')}",
        }
    
    