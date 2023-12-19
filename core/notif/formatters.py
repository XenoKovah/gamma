"""Message formatters for different providers."""

import json

def json_formatter(data):
    """
    Format message data to JSON format.
    """
    return json.dumps({
        'title': data.get('head'),
        'description': data.get('body'),
    })

