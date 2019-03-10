import os
import json
from flask import(
    Flask,request,abort
)

from linebot import(
    LineBotApi,WebhookHandler
)

from linebot.exceptions import(
    InvalidSignatureError
)

from linebot.models import(
    MessageEvent,TextMessage,TextSendMessage,
    StickerMessage,StickerSendMessage
)

app = Flask(__name__)

lineBotApi = LineBotApi('xMJm2PyVKN4v0Z1hDHZxQZ3wjtu9uVADZvURZj4mVll3lZVDfO6v822eAbxnD6JA5aH8rsmMU/x7N3tAp2V0rnGM5hRkazcXObYt/85reI9zamVVp7BfqTja193ycCETfNMyTh592YN20+Ec1/HBlwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3f5bd8450f7e556bedb854b3cf284775')

@app.route("/webhook",methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def handle_text_message(event):
    lineBotApi.reply_message(event.reply_token,TextSendMessage(text=event.message.text))

@handler.add(MessageEvent,message=StickerMessage)
def handle_sticker_message(event):
    lineBotApi.reply_message(event.reply_token,StickerSendMessage(package_id=event.message.package_id,sticker_id=event.message.sticker_id))

if __name__ == "__main__":
    port = int(os.environ.get('PORT',1234))
    app.run(host='0.0.0.0',port=port,debug=True)
