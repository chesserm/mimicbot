# utils.py
import json 

SEP = "[SEP]"
PAD = "[PAD]"
BOS = "[BOS]"
EOS = "[EOS]"
LOWER_CASE = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
NUMBERS = [str(x) for x in range(0, 10)]
PUNCUATION_OTHER = [" ", ".", "?",  ",", "'", "!", "@", '%', '\n', ':', ';']
IMG_TOKEN = "[IMG]"
GIF_TOKEN = "[GIF]"
LINK_TOKEN = "[LINK]"

# Load emotes file
with open("custom/emotes.txt", 'r') as fp:
    VALID_EMOTES = [x.strip() for x in fp.readlines()]


def read_json(json_filename : str) -> dict:
    """
    JSON read helper
    """
    with open(json_filename, 'r')  as fp:
        file_data = fp.read()
    return json.loads(file_data)


def write_json(json_dict : dict, out_file : str) -> None:
    """
    JSON write helper
    """
    with open(out_file, 'w') as out_fp:
        out_fp.write(json.dumps(json_dict, indent=4))

    return 


def read_jsonl(filename : str) -> list:
    """
    Reads .jsonl file
    """

    with open (filename, 'r') as fp:
        jsonl_data = [json.loads(x) for x in fp.readlines()]
    
    return jsonl_data


def load_secrets(secret_filename:str="custom/secrets.json") -> dict:
    """
    Helper to load the secrets file. 
    """
    secrets = read_json(secret_filename)

    return secrets