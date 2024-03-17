import logging
import redis
import configparser
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler,filters

from ChatGPT_HKBU import HKBU_ChatGPT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class TelegramBot:
    def __init__(self,config_file = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.redis1 = redis.Redis(host=config['REDIS']['HOST'], port=config['REDIS']['PORT'], db=0, password=config['REDIS']['PASSWORD'])
        self.chatgpt = HKBU_ChatGPT(config)
        self.application = ApplicationBuilder().token(config["TELEGRAM"]["ACCESS_TOKEN"]).build()

    # 下方的async开头的函数是Telegram Bot API规定的函数格式，用于处理用户发送的消息，可以根据实际需求进行新增、改写
    # update: 用户发送的消息 context: 上下文
    async def start(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 定义一个start函数，后面会跟/start命令进行关联，当用户发送/start命令时，使用该函数回复一条消息，信息内容为text
        # chat_id为用户发送消息的会话ID,text为回复的消息内容
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me! you can use /help to see what I can do!")

    async def caps(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 课件中的示例函数，后面会跟/caps命令进行关联，将用户发送的消息转换为大写，并发送回去
        if len(context.args) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide some text to capitalize!")
            return
        text_caps = ' '.join(context.args).upper()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

    async def add(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 课件中的示例函数，后面会跟/add命令进行关联，使用redis统计命令后面的消息出现了多少次
        if len(context.args) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide some text to capitalize!")
            return
        msg = context.args[0]
        self.redis1.incr(msg)
        await update.message.reply_text(f'you have said {msg} for {self.redis1.get(msg).decode("UTF-8")} times')

    def parse_msg(self,update,msg):
        # 这个函数从redis中读取对应用户之前的对话记录，以保持上下文
        user_id = update.get_bot().id
        content = self.redis1.get(str(user_id))
        if content:
            content = json.loads(content)
            content.extend(msg)
        else:
            content = msg
        reply_message = self.chatgpt.submit(content)
        content.append(reply_message)
        # print(content)
        self.redis1.set(user_id, json.dumps(content))
        return reply_message['content']

    async def equiped_chatgpt(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        # 对接chatgpt的函数，将用户的消息，通过chatgpt接口发送出去，并获取chatgpt的回复，然后发送给用户
        msg = [{"role": "user", "content": update.message.text}]
        reply_message = self.parse_msg(update,msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

    async def mark(self,update,context):
        msg = [
            # {"role":"system","content":"你是一个书评及影视作者，当我给你一本书名或者一部电影时，请给出打分及评论，满分是10分"},
            {"role":"user","content":f"我给你一本书或者一部电影的标题，你需要先给出评分，然后介绍并评论，标题是：{context.args[0]}"}
        ]
        reply_message = self.parse_msg(update,msg)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

    async def help(self,update,context):
        text = '''/start 开始对话
        /reset 重置对话
        /mark 评分及评论
        /help 帮助
        /caps 转大写
        '''
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    async def reset(self,update,context):
        user_id = update.get_bot().id
        self.redis1.delete(user_id)
        await self.start(update,context)


    def main(self):
        # 创建一个MessageHandler，处理用户发送的消息，筛选出用户的文本或命令，并将筛选出的内容，交给equiped_chatgpt处理，即让chatgpt进行答复
        self.application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.equiped_chatgpt))
        # 创建一个CommandHandler，处理用户发送的命令，当用户发送/start命令时，调用start函数
        self.application.add_handler(CommandHandler('start', self.start))
        # 创建一个CommandHandler，处理用户发送的命令，当用户发送/add命令时，调用add函数
        self.application.add_handler(CommandHandler('add', self.add))
        # 创建一个CommandHandler，处理用户发送的命令，当用户发送/caps命令时，调用caps函数
        self.application.add_handler(CommandHandler('caps', self.caps))
        self.application.add_handler(CommandHandler('mark', self.mark))
        self.application.add_handler(CommandHandler('help', self.help))
        self.application.add_handler(CommandHandler('reset', self.reset))

        # 启动
        self.application.run_polling()



if __name__ == '__main__':
    tel_chatgpt_bot = TelegramBot()
    tel_chatgpt_bot.main()
