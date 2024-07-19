import json
import time
import requests
from config import conf
from common.log import logger


class CozeProcessor:
    def __init__(self):
        pass

    def summary_image(self, session_id: str, file_id: str, prompt="总结这张图中的内容"):
        logger.debug(f"[Coze Wrapper] summary_file enter")
        conversation_id, chat_id = self.start_conversation(session_id, file_id, prompt)
        if conversation_id and chat_id:
            status = self.check_conversation_status(conversation_id, chat_id)
            if status == 'completed':
                return self.get_answer_content(conversation_id, chat_id)
            else:
                logger.warn("[Coze Wrapper] Summary Error, status={}".format(status))
                return None
    
    def solve_problem(self, session_id: str, file_id: str, prompt="解决这张图中的问题"):
        logger.debug(f"[Coze Wrapper] solve_problem enter")
        conversation_id, chat_id = self.start_conversation(session_id, file_id, prompt)
        if conversation_id and chat_id:
            status = self.check_conversation_status(conversation_id, chat_id)
            if status == 'completed':
                return self.get_answer_content(conversation_id, chat_id)
            else:
                logger.warn("[Coze Wrapper] Solve Error, status={}".format(status))
                return None
    
    def redraw_image(self, session_id: str, file_id: str, style:str, prompt="重绘这张图"):
        logger.debug(f"[Coze Wrapper] redraw_image enter")
        text = prompt
        if style:
            text = f"{prompt}, 风格为：{style}"
        conversation_id, chat_id = self.start_conversation(session_id, file_id, text)
        if conversation_id and chat_id:
            status = self.check_conversation_status(conversation_id, chat_id)
            if status == 'completed':
                return self.get_answer_content(conversation_id, chat_id)
            else:
                logger.warn("[Coze Wrapper] Redraw Error, status={}".format(status))
                return None
    
    def finetune_image(self, session_id: str, file_id: str, tip: str, prompt="微调这张图内容"):
        logger.debug(f"[Coze Wrapper] finetune_image enter")
        text = prompt
        if tip:
            text = f"{prompt}, 微调的要求是：{tip}"
        conversation_id, chat_id = self.start_conversation(session_id, file_id, text)
        if conversation_id and chat_id:
            status = self.check_conversation_status(conversation_id, chat_id)
            if status == 'completed':
                return self.get_answer_content(conversation_id, chat_id)
            else:
                logger.warn("[Coze Wrapper] Finetune Error, status={}".format(status))
                return None
    
    def analysis_image(self, session_id: str, file_id: str, prompt="分析这张图中数据"):
        logger.debug(f"[Coze Wrapper] analysis_image enter")
        conversation_id, chat_id = self.start_conversation(session_id, file_id, prompt)
        if conversation_id and chat_id:
            status = self.check_conversation_status(conversation_id, chat_id)
            if status == 'completed':
                return self.get_answer_content(conversation_id, chat_id)
            else:
                logger.warn("[Coze Wrapper] Analysis Error, status={}".format(status))
                return None


    # 发起对话
    def start_conversation(self, session_id, file_id, text):
        url = f"{self.base_url()}/chat"
        headers = self.headers()
        payload = self.get_payload(session_id, file_id, text)
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        logger.debug(f"[Coze Wrapper] start_conversation response , response={response_json}")
        if response.status_code == 200:
            if response_json.get("code") == 0:
                data = response_json.get("data")
                conversation_id = data.get('conversation_id')
                chat_id = data.get('id')
                return conversation_id, chat_id
            else:
                error_msg = response_json.get("msg")
                error_code = response_json.get("code")
                logger.warn(f"[COZE Wrapper] Response Error text={error_msg} status_code={error_code}")
                return None, None
                
        else:
            error_info = f"[COZE Wrapper] Response Network Error text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None, None

    # 轮询查询对话状态
    def check_conversation_status(self, conversation_id, chat_id):
        url = f'{self.base_url()}/chat/retrieve'
        headers = self.headers()
        params = {
            'conversation_id': conversation_id,
            'chat_id': chat_id
        }
        while True:
            response = requests.get(url, headers=headers, params=params)
            response_json = response.json()
            logger.debug(f"[Coze Wrapper] check_conversation_status response, url={url} response={response_json}")
            if response.status_code == 200:
                if response_json.get("code") == 0:
                    data = response_json.get("data")
                    status = data.get('status')
                    if status in ['completed', 'failed']:
                        return status
                    logger.warn("[Coze Wrapper] conversation status is not completed, status={}".format(status))
                    # 假设轮询间隔为5秒
                    time.sleep(6)
                else:
                    error_msg = response_json.get("msg")
                    error_code = response_json.get("code")
                    logger.warn(f"[COZE Wrapper] Response Error text={error_msg} status_code={error_code}")
            else:
                error_info = f"[COZE Wrapper] response text={response.text} status_code={response.status_code}"
                logger.warn(error_info)
            

    # 获取Answer内容
    def get_answer_content(self, conversation_id, chat_id):
        url = f"{self.base_url()}/chat/message/list"
        headers = self.headers()
        params = {
            'conversation_id': conversation_id,
            'chat_id': chat_id,
        }
        response = requests.get(url, headers=headers, params=params)
        response_json = response.json()
        logger.info(f"[Coze Wrapper] get_answer_content response, response={response_json}")
        if response.status_code == 200:
            if response_json.get("code") == 0:
                data = response_json.get("data")
                answer = None
                for message in data:
                    if message.get('type') == 'answer':
                        answer = message.get('content')
                        break
                return {
                    'answer': answer,
                }
            else:
                error_msg = response_json.get("msg")
                error_code = response_json.get("code")
                logger.warn(f"[COZE Wrapper] Response Error text={error_msg} status_code={error_code}")
                return None
        else:
            error_info = f"[COZE Wrapper] Network Error text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None


    def base_url(self):
        return "https://api.coze.cn/v3"


    def headers(self):
        return {
            'Authorization': f"Bearer {conf().get('coze_api_key', '')}",
        }
    
    def get_payload(self, session_id: str, file_id: str, text: str):
            if file_id is None:
                return None
            logger.info(f"[Coze Wrapper] get_payload enter,  file_id={file_id}")
            content = [
                    {
                        "type": "image",
                        "file_id": file_id,
                    },
                    {
                        "type": "text",
                        "text": text
                    }
            ]
            json_str = json.dumps(content, ensure_ascii=False)
            logger.info(f"[Coze Wrapper] get_payload , json_str={json_str}")
            payload =  {
                        "bot_id": "7388480821546106918",
                        "user_id": session_id,
                        "stream": False,
                        "auto_save_history":True,
                        "additional_messages":[{
                                "role":"user",
                                "content":json_str,
                                "content_type":"object_string"
                                }]
                        }
            return payload
    


    def check_file(self, file_path: str) -> bool:
        suffix = file_path.split(".")[-1]
        # 后缀小写处理
        suffix = suffix.lower()
        support_list = ["jpg", "jpeg", "png"]
        if suffix not in support_list:
            logger.warn(f"[Coze Wrapper] Unsupported File, suffix={suffix}, support_list={support_list}")
            return False

        return True

    