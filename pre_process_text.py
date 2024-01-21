from utils import read_json, load_secrets, BOS, SEP, EOS, IMG_TOKEN, GIF_TOKEN, LINK_TOKEN
from datetime import timedelta
from dateutil import parser
import re
import json

FOLDER = "messages"
emote_re = re.compile("(?=:).+(?=:.*\>)")

def break_into_conversations(full_json : dict, time_delta_threshold:int=10) -> list:
    """
    Breaks messages into conversations. 

    Takes all messages received and chunks them into conversations. 

    Input:
        - full_json: The full json of all scraped messages. Output of downloader.py
        - time_delta_threshold: A threshold for determining how much time can occur between messages 
                                in the same conversation (in minutes).

    Output:
        - convos: A list of convos (each a lists of strings), representing messages 
                    in the conversation (ordered by time - index 0 is first message)
    """
    convos = []
    current_convo = None 
    prev_message_time = None 

    # Full JSON is sorted in reverse order
    for mssg_idx in range(len(full_json) - 1, -1, -1):
        message = full_json[mssg_idx]
        
        # https://www.geeksforgeeks.org/create-python-datetime-from-string/
        curr_msg_timestamp = parser.parse(message["timestamp"])

        # https://discord.com/developers/docs/resources/channel#message-object-message-types
        is_a_response = message["type"] in [19]
        
        # First Message
        if (current_convo is None ):
            current_convo = [message]
        else:
            is_awhile_after_last = (curr_msg_timestamp - prev_message_time) > timedelta(minutes=time_delta_threshold)

            # New convo conditions: not a reply and at least specified num mins after last message
            if (not is_a_response and is_awhile_after_last):
                convos.append(current_convo)
                current_convo = [message]
            else:
                current_convo.append(message)

        prev_message_time = curr_msg_timestamp

    return convos


def process_msg_text(message:dict) -> str:
    """
    Handles all pre-processing of message text. 

    Input:
        - message: A single message object.
    
    Output:
        - processed_msg: The string of processed message string.
    """
    content = message["content"]
    
    # Empty string implies an image was sent. Consequence of downloader.py's parse_message()
    if (content == ""):
        content = IMG_TOKEN
        return content 
    elif (content.startswith("https://tenor.com/")):
        content = GIF_TOKEN
        return content

    for mention in message["mentions"]:
        content = content.replace(f"<@{mention['id']}>", "@" + mention['username'])

    # Process each word in the message.
    # Replaces emotes with format expected, lower cases text, replaces links with link token. 
    content_tokens = content.split()
    for i in range(len(content_tokens)):
        token = content_tokens[i]

        if (token.startswith("https:")):
            content_tokens[i] = LINK_TOKEN
        else:
            emote_val = re.search(emote_re, token)
            if (emote_val is not None):
                # regexp for this is annoying. Need to add back in the closing : (e.g., :KEKW:)
                content_tokens[i] = emote_val.group(0) + ":" 
            elif(content_tokens[i] not in [GIF_TOKEN, IMG_TOKEN, LINK_TOKEN]):
                content_tokens[i] = content_tokens[i].lower()
    
    processed_msg = " ".join(content_tokens)
    return processed_msg 


def split_into_user_context(convo:list) -> dict:
    """
    Splits a conversation into context + response pairs for model training.

    Input:
        - convo: A list of strings representing a conversation. First message is assumed to be index 0.

    Output:
        -  author_data : Dictionary mapping author (str) to list of context response pairs, where the corresponding
                        author is the one who responded.
    """
    # This combines all contiguous user messages into one string.
    # Often times in discord, users will split their response into several individual message. This corrects that.
    # Separate messages denoted by periods.
    combined_messages = []
    prev_author = None 
    curr_message = ""
    for message in convo:
        author = message["author"]["username"]
        message_content = process_msg_text(message)

        if (author == prev_author or prev_author is None ):
            curr_message += message_content + ". "
        else:
            combined_messages.append({
                "author" : prev_author, 
                "message" : curr_message
            })
            curr_message = message_content + ". "        
        prev_author = author 

    # Can't forget the final message
    combined_messages.append({
                "author" : prev_author, 
                "message" : curr_message
            })
    
    # Split these messages into context + response pairs.
    author_data = {}
    prev_context = " "
    all_prev_context = ""
    for message in combined_messages:
        author = message["author"]
        message_content = message["message"]

        if (author not in author_data):
            author_data[author] = []
        
        # Format for model training: "[BOS] {prompt} [SEP] {response} [EOS]"
        train_string = f"{BOS} " + prev_context + f" {SEP} " + message_content + f" {EOS}"

        # Format as jsonl
        author_data[author].append( json.dumps({"context" : prev_context, "response" : message_content, "train" : train_string}) + "\n" )
        prev_context = message_content
        all_prev_context += message_content
    
    return author_data


def main():
    secrets = load_secrets()
    user_to_id = secrets["users"]
    
    # File with all messages scraped using downloader.py
    base_message = FOLDER + "/all_messages.json"
    all_msgs_json = read_json(base_message)

    convos = break_into_conversations(all_msgs_json, user_to_id)

    all_author_data = {}
    for convo in convos:
        author_data = split_into_user_context(convo)

        for author, data in author_data.items():
            if (author not in all_author_data):
                all_author_data[author] = data 
            else:
                all_author_data[author] += data
    
    # Write each author's data to their own .jsonl file.
    # NOTE: discord usernames can have periods in them. Deal with that as you need to.
    for author, all_data in all_author_data.items():
        with open(FOLDER + f"/user_messages/{author}.jsonl", 'w') as fp:
            fp.writelines(all_data)



if (__name__ == "__main__"):
    main()