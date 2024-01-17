import requests
import json 
import time
from utils import load_secrets, write_json


def get_messages(channel_id:str, num_messages:int=100, before_message_id:str=None, headers:dict=None) -> dict:
    """
    Scrapes messages
    """

    if (before_message_id is None):
        response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages?limit={num_messages}", headers=headers)
    else:
        response = requests.get(f"https://discord.com/api/v8/channels/{channel_id}/messages?limit={num_messages}&before={before_message_id}", headers=headers)
    res_json = json.loads(response.text)
    return res_json


def parse_message(res_message:dict) -> dict:
    """
    Slims down message response into fields we care about
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


    # Get first batch of jsons
    final_out_json = []
    message_id = None 

    iter_count = 0
    try:
        while True:
            time.sleep(1)

            # Get the messages
            out_json = get_messages(channel_id, before_message_id=message_id, headers=headers)

            # Last message id (used for pagination on next request above)
            message_id = out_json[-1]["id"]
            
            for res_message in out_json:
                final_out_json.append(parse_message(res_message))
            
            iter_count += 1
            if (iter_count % 100 == 0):
                print(f"Finished iteration: {iter_count}")
    except Exception as e:
        print(f"caught exception: {e}")
    finally:
        write_json(final_out_json, "messages.json")


if __name__ == "__main__":
    main()