import os
from decouple import(
    config
)
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

lineBotApi = LineBotApi(config("LINE_CHANNEL_ACCESS_TOKEN",default=os.environ.get('LINE_ACCESS_TOKEN')))
handler = WebhookHandler(config("LINE_CHANNEL_SECRET",default=os.environ.get('LINE_CHANNEL_SECRET')))

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
