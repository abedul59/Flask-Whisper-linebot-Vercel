# -*- coding: utf-8 -*-

import logging
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, AudioMessage
from linebot.models import TextSendMessage, ImageSendMessage
import os

from flask import Flask, request



#################
import openai
	
openai.api_key = os.getenv("OPENAI_API_KEY")
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
#parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET")) 


	


class Whisper:  
    

    def __init__(self):
        
        self.transcribed_text = ""



    def get_response(self, audio_file):
        #import openai
        #openai.api_key = openai.api_key
        response = openai.Audio.transcribe(
            model = "whisper-1",
            file = audio_file
            )
        self.transcribed_text = response['text']
        print(self.transcribed_text)


        
        return self.transcribed_text
	



whisper = Whisper()

app = Flask(__name__)


@app.route("/")
def hello():
	return "Hello World from Flask in a uWSGI Nginx Docker container with \
	     Python 3.8 (from the example template)"
         
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=AudioMessage)
def handle_AudioMessage(event):
    # Get user's message
    #user_message = event.message.text
    try:
        if (event.message.type == "audio"):
            audio_content = line_bot_api.get_message_content(event.message.id)
            path = "./temp.mp3"
            print("路徑為temp.mp3")
            with open(path, "wb") as fd:
                for chunk in audio_content.iter_content():
                    fd.write(chunk)
            print("寫入temp.mp3完成！")
            #fd.close()
            #import time
            #time.sleep(1)

            with open("temp.mp3", "rb") as audio_file:
                result_text = whisper.get_response(audio_file)
            print("得到whisper結果！")
            print(result_text)
 	    



            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= result_text)
            )

    except:
        pass


if __name__ == '__main__':
	    app.run(debug=True, port=os.getenv("PORT", default=5000))
