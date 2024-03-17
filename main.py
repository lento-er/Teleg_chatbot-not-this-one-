import logging
import redis
import configparser
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler,filters

from ChatGPT_HKBU import HKBU_ChatGPT

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

config = configparser.ConfigParser()
config.read('config.ini')



redis1 = redis.Redis(host=config['REDIS']['HOST'], port=config['REDIS']['PORT'], db=0, password=config['REDIS']['PASSWORD'])
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 当用户发送/start命令时，回复一条消息
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 当用户发送任何消息时，回复相同的消息
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 将用户发送的消息转换为大写，并发送回去
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide some text to capitalize!")
        return
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = context.args[0]
    redis1.incr(msg)
    await update.message.reply_text(f'you have said {msg} for {redis1.get(msg).decode("UTF-8")} times')

async def equiped_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_message = chatgpt.submit(update.message.text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(config["TELEGRAM"]["ACCESS_TOKEN"]).build()
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), equiped_chatgpt)
    start_handler = CommandHandler('start', start)
    # 创建一个MessageHandler，处理用户发送的消息，主要过滤用户的文本或命令，并使用echo函数处理消息
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)
    add_handler = CommandHandler('add', add)
    application.add_handler(start_handler)
    # application.add_handler(echo_handler)
    application.add_handler(caps_handler)
    application.add_handler(add_handler)
    application.add_handler(chatgpt_handler)


    application.run_polling()