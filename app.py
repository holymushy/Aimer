import datetime
import json
import os
import logging
import re

from flask import Flask, make_response, request
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

import bot

import interaction

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['JAWSDB_URL']
db = SQLAlchemy(app)

import coffee
import hanabi
import tea

pyBot = bot.Bot()
client = pyBot.client

processed_messages = []


@app.route("/tea", methods=["GET", "POST"])
def process_tea():
    time = process_event_time(request)
    tea.get_tea(time)
    return make_response(f"Requested tea time at {time}", 200,)


@app.route("/coffee", methods=["GET", "POST"])
def process_coffee():
    time = process_event_time(request)
    coffee.get_coffee(time)
    return make_response(f"Requested coffee time at {time}", 200,)


@app.route("/hanabi", methods=["GET", "POST"])
def process_hanabi():
    time = process_event_time(request)
    hanabi.get_hanabi(time)
    return make_response(f"Requested hanabi time at {time}", 200,)


def process_event_time(request):
    text = request.form['text'].lower().strip()
    print(text)
    params = text.split()
    time_pattern = re.compile("@?([0-9]+)([pa]m)")

    time = None

    for p in params:
        p = p.strip()
        m = time_pattern.match(p)
        if m:
            time = m.group(0)
            if time[0] == "@":
                time = time[1:]
            break

    if not time:
        next_hour = datetime.datetime.now(tz=timezone('US/Pacific')) + datetime.timedelta(hours=1)
        if next_hour.hour > 12:
            time = f"{next_hour.hour-12}pm"
        elif next_hour.hour == 12:
            time = "12pm"
        elif next_hour.hour == 0:
            time = "12am"
        else:
            time = f"{next_hour.hour}am"

    return time


@app.route("/encourage", methods=["GET", "POST"])
def encourages():
    text = request.form['text'].strip()
    print(text)
    recipient = None
    params = text.split()
    username_pattern = re.compile("<[@#](\w+)(|.+)?>")

    for p in params:
        p = p.strip()
        m = username_pattern.match(p)
        if m:
            recipient = m.group(1)
            recipient_name = m.group(2)[1:]
            break

    if recipient:
        remaining = text.replace(p, '').strip()
        if not remaining:
            remaining = "You got this!"
        pyBot.reply(remaining, recipient)
    return make_response(f"Sent encouragement for {recipient_name}", 200,)

@app.route("/", methods=["GET", "POST"])
def listens():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    # if request.get('payload'):
    payload = request.form.to_dict().get('payload')
    if payload:
        response = json.loads(payload)
        print(response)

        actions = response["actions"]
        ts = response["original_message"]["ts"]
        channel = response["channel"]["id"]
        new_response = response["original_message"]["attachments"].copy()
        for a in actions:
            if not new_response[0].get("footer"):
                new_response[0]["footer"] = ""

            footer = new_response[0]["footer"]

            start = footer.find(response["user"]["name"])
            if start != -1:
                end = footer.find("\n", start)
                new_response[0]["footer"] = footer[:start] + footer[end+1:]

            new_response[0]["footer"] += f'{response["user"]["name"]} voted {a["value"]}\n'
            pyBot.update(ts, response["original_message"]["text"], new_response, channel)
            if new_response[0]["footer"].count("yes :+1:") >= 3:
                pyBot.reply("<!channel> More than 3 people voted `yes`. Let's do it!", channel)

        return make_response("Processed interactive message", 204,)

    slack_event = json.loads(request.data)
    print(slack_event)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """
    if event_type == "message":
        # Ignore the bot's own messages
        received_message = slack_event["event"].get("text")
        if received_message and not slack_event["event"].get("bot_id"):
            message_id = slack_event["event"].get("client_msg_id")
            if message_id in processed_messages:
                return make_response("Already processed message", 200,)
            processed_messages.append(message_id)
            is_dm = slack_event["event"].get("channel_type") == "im"
            if is_dm:
                interaction.reply(
                    received_message, slack_event["event"].get("channel"), is_dm
                )
            else:
                interaction.reply(
                    received_message, slack_event["event"].get("user"), is_dm
                )
        return make_response("Processed message", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 500, {"X-Slack-No-Retry": 1})


if __name__ == '__main__':
    app.run(debug=True)
