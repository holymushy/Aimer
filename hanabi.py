import os

from app import db

import bot

pyBot = bot.Bot()

hanabi_channel = os.environ['HANABI_CHANNEL']

attachments_json = [
    {
        "fallback": "Oops. Something went wrong.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "hanabi_vote",
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

def get_hanabi(time):
	pyBot.reply_with_attachment(f":hanabi: @ {time}?", hanabi_channel, attachments_json)
