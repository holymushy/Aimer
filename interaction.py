import bot
import json
import random

with open('KW_response_phrases.json', 'r') as handle:
    fixed_json = ''.join(line for line in handle if not line.strip().startswith('//'))
    data = json.loads(fixed_json)
    group_do_response = data["group_do_response"]
    group_no_response = data["group_no_response"]

pyBot = bot.Bot()

DEFAULT_RESPONSES = [
    "I’m sorry, I was deep in thought. Can you say that again, only with more detail?",
    "I’m afraid I don’t understand. Can you explain that?",
    "I’m not sure we have that kind of thing where I come from. Can you tell me more?",
    "My apologies, but could you elaborate?",
    "Would you mind expanding on that?",
    "You don’t say! Tell me more!",
    "I’d love to hear more about that. Maybe I can help?",
]

def reply(received_message, channel, is_dm):
    """
    @param received_message: the message received from user/channel
    @param channel: the group/user channel that this message came from
    @param is_dm: the flag that indicates whether this message a DM
                  (Direct Message)
    """
    match = False
    response_message = None
    for k in group_do_response.keys():
        if k in received_message.lower():
            response_message = group_do_response[k]
            match = True
            break

    if is_dm and not match:
        for k in group_no_response.keys():
            if k in received_message.lower():
                response_message = group_no_response[k]
                match = True
                break

    if is_dm and not match:
        response_message = random.choice(DEFAULT_RESPONSES)

    if response_message:
        print(response_message)
        pyBot.reply(response_message, channel)
