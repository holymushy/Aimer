# -*- coding: utf-8 -*-
import os

import slack


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

    def reply(self, response_message, channel):
        self.client.chat_postMessage(
            channel=channel,
            as_user=True,
            text=response_message,
        )

    def reply_with_attachment(self, response_message, channel, attachments):
        self.client.chat_postMessage(
            channel=channel,
            as_user=True,
            text=response_message,
            attachments=attachments,
        )

    def update(self, ts, text, attachments, channel):
        self.client.chat_update(
            channel=channel,
            as_user=True,
            ts=ts,
            attachments=attachments,
            text=text,
        )
