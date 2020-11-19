import requests
import logging
from datetime import datetime
from flask import json


def xkcd_bot(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    data = request.get_json()

    resp_dict = None

    if data['type'] == 'REMOVED_FROM_SPACE':
        logging.info('Bot removed from a space')

    else:
        resp_dict = format_response(data)

    return json.jsonify(resp_dict)


def format_response(event):
    """Determine what response to provide based upon event data.
    Args:
      event: A dictionary with the event data.
    """

    message = ""

    # Case 1: The bot was added to a room
    if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
        message = create_text(
            'Thanks for adding me to "%s"! Type "help" for a full list of commands!' % event['space']['displayName'])

    # Case 2: The bot was added to a DM
    elif event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'DM':
        message = create_text(
            'Thanks for adding me to a DM, %s! Type "help" for a full list of commands!' % event['user']['displayName'])

    elif event['type'] == 'MESSAGE':
        message = create_response(event['message']['text'])

    return message


def create_response(message_text):
    if message_text == 'latest':
        message = get_latest()
    elif message_text == 'random':
        message = create_text('I should return a random xkcd!')
    elif message_text == 'number':
        message = 'I should return xkcd with number'
    else:
        message = create_text('Your message: "%s"' % message_text)
    return message


def create_text(text):
    return {'text': text}


def get_latest():
    latest = requests.get('https://xkcd.com/info.0.json')
    latest_json = latest.json()
    card = make_xkcd_card(latest_json)
    return card


def get_latest_num():
    latest = requests.get('https://xkcd.com/info.0.json')
    latest_json = latest.json()
    return latest_json['num']


def make_xkcd_card(data):
    xkcd_base_link = 'https://xkcd.com/'
    explain_base_link = 'https://www.explainxkcd.com/wiki/index.php/'
    title = data['title']
    date = datetime(int(data['year']), int(data['month']), int(data['day']))
    number = str(data['num'])
    image_url = data['img']
    xkcd_link = xkcd_base_link + number
    explain_link = explain_base_link + number

    card_dict = {
        "cards": [
            {
                "header": {
                    "title": "%s" % title,
                    "subtitle": "xkcd No. %s" % number,
                    "imageUrl": "https://www.userlogos.org/files/logos/signify/xkcd.png"
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": "Added on:",
                                    "content": "%s" % date.strftime('%B %d,%Y')
                                }
                            }
                        ]
                    },
                    {"widgets": [
                        {
                            "image": {
                                "imageUrl": "%s" % image_url,
                                "onClick": {
                                    "openLink": {
                                        "url": "%s" % xkcd_link
                                    }
                                }
                            }
                        }
                    ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "EXPLAIN",
                                            "onClick": {
                                                "openLink": {
                                                    "url": "%s" % explain_link
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    return card_dict
