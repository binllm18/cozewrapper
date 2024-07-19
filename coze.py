import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *
from .image_processor import CozeProcessor
from .image_uploader import CozeUploader
from common.expired_dict import ExpiredDict

import os
from config import plugin_config
from common.expired_dict import ExpiredDict

@plugins.register(
    name="CozeWrapper",
    desc="A plugin wrapper of coze.",
    version="0.0.1",
    author="彬子",
    desire_priority=86
)
class CozeWrapper(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[CozeWrapper] inited.")
        except Exception as e:
            logger.warn("[CozeWrapper] init failed, ignore.")
            raise e
        self.config = super().load_config()
        if not self.config:
            logger.info(f"[CozeWrapper] Config global load fail")
            self.config = self._load_config_template()
        logger.info(f"[CozeWrapper] Config load template file, config={self.config}")
        self.params_cache = ExpiredDict(300)

    def on_handle_context(self, e_context: EventContext):
        """
        消息处理逻辑
        :param e_context: 消息上下文
        """
        if not self.config:
            return

        context = e_context['context']
        if context.type in [ContextType.IMAGE]:
            # filter content no need solve
            # 文件处理
            context.get("msg").prepare()
            image_path = context.content
            if not CozeProcessor().check_file(image_path):
                return
            _send_info(e_context, "正在上传，请稍后")
            session_id = context["session_id"]
            file_id = self._get_file_id(session_id, image_path)
            reply_text = self._get_process_text(file_id, "已完成上传，你想对图片做何操作：")
            _set_reply_text(reply_text, e_context, level=ReplyType.TEXT)
            os.remove(image_path)
            
        elif context.type in [ContextType.TEXT]:
            # 文本处理
            context.get("msg").prepare()
            content = context.content
            content_split = content.split(":")
            logger.info(f"[CozeWrapper] content_split, content={content}  content_split={content_split}")
            if len(content_split) < 2 or content_split[0] not in self._get_process_config():
                return
            session_id = context["session_id"]
            file_id = content_split[1]
            if content_split[0] == self.config["summary_image"]["instruct"]:
                _send_info(e_context, "正在总结，请稍后")
  
                res = CozeProcessor().summary_image(session_id, file_id, self.config["summary_image"]["prompt"])
                if not res:
                    _set_reply_text("因为神秘力量无法总结内容，请稍后再试吧", e_context, level=ReplyType.TEXT)
                summary_text = res.get("answer")
                _set_reply_text(summary_text, e_context, level=ReplyType.TEXT)

            elif content_split[0] == self.config["solve_problem"]["instruct"]:
                _send_info(e_context, "正在解答，请稍后")
                res = CozeProcessor().solve_problem(session_id, file_id, self.config["solve_problem"]["prompt"])
                if not res:
                    _set_reply_text("因为神秘力量无法解答习题，请稍后再试吧", e_context, level=ReplyType.TEXT)
                answer_content = res.get("answer")
                _set_reply_text(answer_content, e_context, level=ReplyType.TEXT)

            elif content_split[0] == self.config["redraw_image"]["instruct"]:
                _send_info(e_context, "正在重绘，请稍后")
                style = None
                if len(content_split) == 3:
                    style = content_split[2]
                res = CozeProcessor().redraw_image(session_id, file_id, style, self.config["redraw_image"]["prompt"])
                if not res:
                    _set_reply_text("因为神秘力量无法重绘图片，请稍后再试吧", e_context, level=ReplyType.TEXT)
                redraw_content = res.get("answer")
                _set_reply_text(redraw_content, e_context, level=ReplyType.TEXT)

            elif content_split[0] == self.config["finetune_image"]["instruct"]:
                _send_info(e_context, "正在微调，请稍后")
                text = None
                if len(content_split) == 3:
                    text = content_split[2]
                res = CozeProcessor().finetune_image(session_id, file_id, text, self.config["finetune_image"]["prompt"])
                if not res:
                    _set_reply_text("因为神秘力量无法微调图片，请稍后再试吧", e_context, level=ReplyType.TEXT)
                finetune_content = res.get("answer")
                _set_reply_text(finetune_content, e_context, level=ReplyType.TEXT)
                
            elif content_split[0] == self.config["analysis_image"]["instruct"]:
                _send_info(e_context, "正在分析，请稍后")
                res = CozeProcessor().analysis_image(session_id, file_id, self.config["analysis_image"]["prompt"])
                if not res:
                    _set_reply_text("因为神秘力量无法分析图片，请稍后再试吧", e_context, level=ReplyType.TEXT)
                analysis_content = res.get("answer")
                _set_reply_text(analysis_content, e_context, level=ReplyType.TEXT)
            

    def _load_config_template(self):
        try:
            config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    congfig = json.load(f)
                    plugin_config["coze_wrapper"] = congfig
                    return congfig
            else:
                logger.warn("No CozeWrapper plugin config.json, copy plugins/coze_wrapper/config.json.template")
        except Exception as e:
            logger.exception(e)
    
    def _get_file_id(self, session_id: str, file_path: str):
        logger.info(f"[CozeWrapper] get_file_id, user={session_id}, path={file_path}")
        if not file_path:
            return None
        if self.params_cache.get(session_id) is None:
            self.params_cache[session_id] = {}
        file_id = self.params_cache.get(session_id).get(file_path)
        if file_id is None:
            file_id = CozeUploader().upload_file(session_id, file_path)
            self.params_cache[session_id][file_path] = file_id
        else:
            logger.info(f"get file id from cache, user={session_id}, path={file_path}")
        return file_id

    def reload(self):
        self.config = super().load_config()
    
    def _get_process_text(self, file_id: str, text: str):
        process_items = [text]
        # 遍历 self.config 里的所有配置
        for key, value in self.config.items():
            if value["enable"]:
                if key == "redraw_image" or key == "finetune_image":
                    process_items.append(value["instruct"]+":"+file_id+":"+("<你需要的风格>" if key == "redraw_image" else "<你的微调指令>"))
                else:
                    process_items.append(value["instruct"]+":"+file_id)
        return '\n'.join(process_items)
    
    def _get_process_config(self):
        process_items = []
        # 遍历 self.config 里的所有配置
        for key, value in self.config.items():
            if value["enable"]:
                process_items.append(value["instruct"])
        return process_items
            


def _send_info(e_context: EventContext, content: str):
    reply = Reply(ReplyType.TEXT, content)
    channel = e_context["channel"]
    channel.send(reply, e_context["context"])


def _set_reply_text(content: str, e_context: EventContext, level: ReplyType = ReplyType.ERROR):
    reply = Reply(level, content)
    e_context["reply"] = reply
    e_context.action = EventAction.BREAK_PASS

