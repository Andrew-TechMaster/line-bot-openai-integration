# Import necessary libraries
import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from linebot_handler import LinebotHandler

load_dotenv()  # Load environment variables from .env file
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# Create a Flask app object
app = Flask(__name__)

# Configure the Line Bot API and Channel Secret
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Create the Message Handler Instance
linebot_handler = LinebotHandler()

# Define a dictionary to track users who received the welcome message
received_welcome = {}

# Function to handle incoming messages
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    if user_id not in received_welcome:
        user_profile = line_bot_api.get_profile(user_id)
        display_name = user_profile.display_name
       
        welcome_message = f"Hi {display_name}, welcome to our chatbox!\n\n"
        welcome_message += "I'm here to assist you. Whether you're new or returning after a server restart, feel free to ask anything!"
        # Send the personalized welcome message
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=welcome_message)
        )

        # Mark the user as having received the welcome message
        received_welcome[user_id] = True

    # Handle other messages or logic
    linebot_handler.handle_message(event, line_bot_api)

# Function to handle postback events
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    linebot_handler.handle_postback(user_id, data, event, line_bot_api)

# Route to handle incoming webhook events
@app.route("/callback", methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # Get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Main
if __name__ == '__main__':
    # Get the port from environment variable or use the default port 5000
    port = int(os.environ.get('PORT', 5000))
    # Run the app on 0.0.0.0 to listen on all available interfaces
    app.run(host='0.0.0.0', port=port)
