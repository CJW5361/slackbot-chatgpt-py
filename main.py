import os
import requests
from dotenv import load_dotenv
load_dotenv()

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

openai.api_key = os.environ.get("OPENAI_API_KEY")
api_key = 'd6ef07bbe71aeb6c052f95ea3aa90b18'

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{city}의 날씨: {weather}, 온도: {temp}°C"
    else:
        return "날씨 정보를 가져오는 데 실패했습니다."

@app.message("Test")
def test(message, say):
    print(message)
    user = message['user']
    say(f"{user} 님, ChatGPT 테스트입니다.")
# Slack 봇 이벤트 핸들러 예시
@app.message("날씨")
def handle_weather(message, say):
    try:
        city = message['text'].split(' ')[1]  # "날씨 서울" 같은 형식의 메시지를 가정
        weather_info = get_weather(city)
        say(weather_info)
    except Exception as e:
        say(f"에러 발생: {e}")


@app.event("message")
def handle_direct_message(message, say):
    user_input = message['text']
    prompt = f"사용자가 다음과 같이 물었습니다: '{user_input}'. 적절한 대답은 무엇일까요?"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{message['text']}"}]
    )
    
    print(response)
    say(response.choices[0].message.content)

@app.event("app_mention")
def handle_mention(message, say):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{message['text']}"}]
    )
    
    print(response)
    say(response.choices[0].message.content)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
