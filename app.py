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

import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import(
    TfidfVectorizer
)
from sklearn.metrics.pairwise import(
    cosine_similarity
) 

app = Flask(__name__)

f=open("chatbot.txt",'r',errors="ignore")
raw = f.read()

raw = raw.lower()

nltk.download('punkt')
nltk.download('wordnet')

sent_token = nltk.sent_tokenize(raw)
word_token = nltk.word_tokenize(raw)

lemmer = nltk.stem.WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct),None) for punct in string.punctuation) 

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]
def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

# Generating response
def response(user_response):
    robo_response=''
    sent_token.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_token)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I don't understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_token[idx]
        return robo_response



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
    lineBotApi.reply_message(event.reply_token,TextSendMessage(text=response(event.message.text)))

@handler.add(MessageEvent,message=StickerMessage)
def handle_sticker_message(event):
    lineBotApi.reply_message(event.reply_token,StickerSendMessage(package_id=event.message.package_id,sticker_id=event.message.sticker_id))



if __name__ == "__main__":
    port = int(os.environ.get('PORT',1234))
    app.run(host='0.0.0.0',port=port,debug=True)
