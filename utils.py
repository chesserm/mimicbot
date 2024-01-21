# utils.py
import json 

# Custom tokens
SEP = "[SEP]"
PAD = "[PAD]"
BOS = "[BOS]"
EOS = "[EOS]"
IMG_TOKEN = "[IMG]"
GIF_TOKEN = "[GIF]"
LINK_TOKEN = "[LINK]"

# Load emotes file
with open("custom/emotes.txt", 'r') as fp:
    VALID_EMOTES = [x.strip() for x in fp.readlines()]


def read_json(json_filename : str) -> dict:
    """
    JSON read helper

    Input:
        - json_filename: Path to JSON filename
    
    Output:
        - json_obj: Dictionary of JSON contents
    """
    with open(json_filename, 'r')  as fp:
        file_data = fp.read()
    return json.loads(file_data)


def write_json(json_dict : dict, out_file : str) -> None:
    """
    JSON write helper

    Input:
        - json_dict: Python dictionary representing JSON contents.
        - out_file: Filename to write json_dict contents to.
    
    Output:
        - None. (writes to file)
    """
    with open(out_file, 'w') as out_fp:
        out_fp.write(json.dumps(json_dict, indent=4))

    return 


def read_jsonl(filename : str) -> list:
    """
    Reads .jsonl file

    Input:
        - filename: Filename of .jsonl file to read.
    
    Output:
        - jsonl_data : List of dictionaries representing .jsonL data
    """

    with open (filename, 'r') as fp:
        jsonl_data = [json.loads(x) for x in fp.readlines()]
    
    return jsonl_data


def load_secrets(secret_filename:str="custom/secrets.json") -> dict:
    """
    Helper to load the secrets file. 
    
    Created as a separate function for clarity and so users can 
    modify contents in case secrets file is not JSON.

    Input:
        - secret_filename: Filename of the secrets file.
    
    Output:
        - secrets: Secrets as python dictionary.
    """
    secrets = read_json(secret_filename)

    return secrets