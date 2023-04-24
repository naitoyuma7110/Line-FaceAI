import os
from urllib import response

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

from io import BytesIO

from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

YOUR_FACE_API_KEY = os.environ["YOUR_FACE_API_KEY"]
YOUR_FACE_API_ENDPOINT = os.environ["YOUR_FACE_API_ENDPOINT"]

face_client = FaceClient(
    YOUR_FACE_API_ENDPOINT,
    CognitiveServicesCredentials(YOUR_FACE_API_KEY)
    )


app = Flask(__name__)


YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
PERSON_GROUP_ID = os.getenv('KEISUKE_GROUP_ID')
PERSON_ID_AUDREY = os.getenv('PERSON_ID_KEISUKE')


line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    response_msg = '{0}\n顔写真を送って!'.format(event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_msg))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # LINEチャネルを通じてメッセージを返答
    try:
        attr_text = ""
        emotion_text = ""
        valified_text = ""

        # メッセージIDを受け取る
        message_id = event.message.id
        # メッセージIDに含まれるmessage_contentを抽出する
        message_content = line_bot_api.get_message_content(message_id)
        # contentの画像データをバイナリデータとして扱えるようにする
        image = BytesIO(message_content.content)
        
        # Detect from streamで顔検出
        detected_faces = face_client.face.detect_with_stream(
            image, 
            return_face_attributes = ['age','gender','smile','emotion']
        )
        print(detected_faces)
        # 検出結果に応じて処理を分ける
        if detected_faces != []:
            # 検出された顔の最初のIDを取得
            # text = detected_faces[0].face_id

            # 年齢と性別
            age = detected_faces[0].face_attributes.age
            gender = detected_faces[0].face_attributes.gender

            attr_text = '推定年齢:{0}歳\n性別{1}'.format(age,gender)

            # 感情・表情を抽出
            smile = format(detected_faces[0].face_attributes.smile * 100, '.1f')
            anger = format(detected_faces[0].face_attributes.emotion.anger * 100, '.1f')
            contempt = format(detected_faces[0].face_attributes.emotion.contempt * 100, '.1f')
            disgust = format(detected_faces[0].face_attributes.emotion.disgust * 100, '.1f')
            fear = format(detected_faces[0].face_attributes.emotion.fear * 100, '.1f')
            happiness = format(detected_faces[0].face_attributes.emotion.happiness * 100, '.1f')
            neutral = format(detected_faces[0].face_attributes.emotion.neutral * 100, '.1f')
            sadness = format(detected_faces[0].face_attributes.emotion.sadness * 100, '.1f')
            surprise = format(detected_faces[0].face_attributes.emotion.surprise * 100, '.1f')

            emotion_text = '笑顔度:{0}点\n怒り度:{1}点\n侮蔑度:{2}点\n嫌悪度:{3}点\n恐怖度{4}点\n幸せ度:{5}点\n平常度:{6}\n悲しみ度:{7}点\n驚き度:{8}点' \
            .format(smile,anger,contempt,disgust,fear,happiness,neutral,sadness,surprise)

            

            # 顔検出ができたら顔認証を行う
            valified = face_client.face.verify_face_to_person(
                face_id = detected_faces[0].face_id,
                person_group_id = PERSON_GROUP_ID,
                person_id = PERSON_ID_AUDREY
            )
            # 認証結果に応じて処理を変える
            if valified.confidence > 0.7:
                valified_text = 'この顔は完全にTK!\n(TKスコア:{:.3f}点)'.format(valified.confidence * 100)
            elif valified.confidence > 0.5:
                valified_text = 'この顔はほぼTK!\n(TKスコア:{:.3f}点)'.format(valified.confidence * 100)
            elif valified.confidence <= 0.5 :
                valified_text = 'この顔はTKではない\n(TKスコア:{:.3f}点)'.format(valified.confidence * 100)
            else:
                valified_text = 'ごめん識別不能！'
        else:
            # 検出されない場合のメッセージ
            valified_text = "顔が検出できない！これ本当に顔写真？"

        response_text = '{0}\n見た感じ...\n{1}\n\n読み取れる感情は...\n{2}'.format(valified_text,attr_text,emotion_text)
            
    except:
        # エラー時のメッセージ
        response_text = "error"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )

if __name__ == "__main__":
    app.run()
