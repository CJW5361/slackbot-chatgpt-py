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


@app.message("Test")
def test(message, say):
    print(message)
    user = message['user']
    say(f"{user} 님, ChatGPT 테스트입니다.")


@app.event("message")
def handle_direct_message(message, say):

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