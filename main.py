import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
import httpx
from dataclasses import dataclass

# 환경 변수 로드
load_dotenv()

# Slack 봇 초기화
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# OpenAI API 키 설정
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")

# WeatherInfo 데이터 클래스 정의
@dataclass
class WeatherInfo:
    area: str
    temperature_now: str
    temperature_low: str
    temperature_high: str
    weather_today: str

# WeatherInfoParser 클래스 정의
class WeatherInfoParser:
    def getScreenshot(self, keyword=str):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel='chrome')
            page = browser.new_page(viewport={'width': 1980, 'height': 2000})

            page.goto(f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={keyword}')

            weather_info = page.locator('div._tab_flicking')
            weather_info.screenshot(path='info.png')

            browser.close()

    def getWeatherInfo(self, keyword=str):
        resp = httpx.get(f'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={keyword}')

        html = HTMLParser(resp.text)
        area = html.css_first('h2.title').text()
        temperature_now = html.css_first('div._today div.temperature_text strong').text(deep=False)
        temperature_low = html.css('li.today span.lowest')[0].text(deep=False).replace('°', '')
        temperature_high = html.css('li.today span.highest')[0].text(deep=False).replace('°', '')
        weather_today = html.css_first('div._today div.weather_main span').text()

        return WeatherInfo(
            area=area,
            temperature_now=temperature_now,
            temperature_low=temperature_low,
            temperature_high=temperature_high,
            weather_today=weather_today,
        )

# WeatherInfoParser 인스턴스 생성
weather_parser = WeatherInfoParser()

# Slack 봇 이벤트 핸들러
@app.event("message")
def handle_direct_message(message, say):
    text = message['text']
    if text.endswith("날씨"):
        # "getWeatherInfo"로 시작하는 메시지를 처리합니다.
        # 메시지를 분리하여 지역 정보를 추출합니다.
        parts = text.split()
        if len(parts) >= 3:
            location = " ".join(parts[0])  # "서울 군자동 날씨" 부분을 추출합니다.
            # 날씨 정보를 가져옵니다.
            weather_info = weather_parser.getWeatherInfo(location)
            # 날씨 정보를 Slack 메시지로 전송합니다.
            say(f"현재 {weather_info.area}의 날씨: {weather_info.temperature_now}, 최저 기온: {weather_info.temperature_low}, 최고 기온: {weather_info.temperature_high}, 오늘의 날씨: {weather_info.weather_today}")
        else:
            say("올바른 명령 형식은 'getWeatherInfo [지역] 날씨'입니다. 지역 정보를 입력해주세요.")
    else:
        # 기존의 GPT-3 응답 처리
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        say(response.choices[0].message.content)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
