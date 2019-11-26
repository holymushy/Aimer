import os

from app import db

import bot

pyBot = bot.Bot()

coffee_channel = os.environ['COFFEE_CHANNEL']

attachments_json = [
    {
        "fallback": "Oops. Something went wrong.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "coffee_vote",
        "actions": [
            {
                "name": "yes",
                "text": ":+1: Yes",
                "type": "button",
                "value": "yes :+1:"
            },
            {
                "name": "nah",
                "text": ":thumbsdown: Nah",
                "type": "button",
                "value": "nah :thumbsdown:"
            },
            {
                "name": "maybe",
                "text": ":thinking_face: Maybe",
                "type": "button",
                "value": "maybe :thinking_face:",
                "style": "danger"
            },
        ]
    }
]

def get_coffee(time):
	pyBot.reply_with_attachment(f"<!here> Would you like some coffee at {time}? :coffee:", coffee_channel, attachments_json)
