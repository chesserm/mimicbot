import requests
import json 
import time
from utils import load_secrets, write_json


def get_messages(channel_id:str, num_messages:int=100, before_message_id:str=None, headers:dict=None) -> dict:
    """
    Scrapes messages from a discord channel

    Input:
        - channel_id: The channel ID of the channel to scrape.
        - num_messages: How many messages to request.
        - before_message_id: Message ID of the last message scraped (for pagination)
        - headers: Dictionary of header information. 
    
    Output:
        - res_json: The JSON containing the message response from the discord API.
    """

    if (before_message_id is None):
        response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages?limit={num_messages}", headers=headers)
    else:
        response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages?limit={num_messages}&before={before_message_id}", headers=headers)
    res_json = json.loads(response.text)
    return res_json


def parse_message(res_message:dict) -> dict:
    """
    Slims down message response into fields we care about.

    Input:
        - res_message: An individual response message as a dictionary. 
    
    Output:
        - message: The same input message, just slimmed down and slightly reformatted.
    """
    message = {}
    message["id"] = res_message["id"]
    message["content"] = res_message["content"]
    message["timestamp"] = res_message["timestamp"]
    message["type"] = res_message["type"]
    
    message["author"] = {
        "id" : res_message["author"]["id"],
        "username" : res_message["author"]["username"],
        "global_name" : res_message["author"]["global_name"],
    }
    message["mentions"] = res_message["mentions"]
    message["mention_everyone"] = res_message["mention_everyone"]
    message["reactions"] = {}
    if ("reactions" in res_message):
        for reaction in res_message["reactions"]:
            name = reaction["emoji"]["name"]
            count = reaction["count"]
            message["reactions"][name] = count

    return message


def main():
    secrets = load_secrets()
    channel_id = secrets["channels"]["main"]
    headers = secrets["headers"]

    final_out_json = []
    message_id = None 

    iter_count = 0
    try:
        while True:
            # Sleep one second per 100 messages. Proactive rate limiting.
            time.sleep(1)

            # Scrape 100 messages from discord API, paginating after last message.
            out_json = get_messages(channel_id, before_message_id=message_id, headers=headers)            
            for res_message in out_json:
                final_out_json.append(parse_message(res_message))
            
            # Last message id (used for pagination on next request above)
            message_id = out_json[-1]["id"]

            iter_count += 1
            if (iter_count % 100 == 0):
                print(f"Finished iteration: {iter_count}")
    except Exception as e:
        print(f"caught exception: {e}")
    finally:
        write_json(final_out_json, "messages/messages.json")


if __name__ == "__main__":
    main()

