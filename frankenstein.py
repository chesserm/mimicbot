import discord
from discord.ext import commands
from pre_process_text import process_msg_text
from utils import load_secrets, BOS, SEP, EOS

from transformers import AutoTokenizer, AutoModelForCausalLM


class MyClient(discord.Client):

    def __init__(self, intents, username):
        super().__init__(intents=intents)
        self.username = username
        self.tokenizer = AutoTokenizer.from_pretrained(f"pretrained_model/models/gpt2/{username}/tokenizer")
        self.model = AutoModelForCausalLM.from_pretrained(f"pretrained_model/models/gpt2/{username}/model")
        return 
    

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        return 
    

    async def on_message(self, message):

        if (message.content.startswith(f"${self.username}")):
            msg_formatted = {"content" : message.content[1:], "mentions" : [] }
            preprocessed_message = process_msg_text(msg_formatted)
            preprocessed_message = f"{BOS} " + preprocessed_message + '.' if preprocessed_message[-1] != '.' else "" +  f" {SEP} "

            inputs = self.tokenizer(preprocessed_message, return_tensors="pt").input_ids
            outputs = self.model.generate(inputs, 
                                               max_new_tokens=200, 
                                               do_sample=True, 
                                               top_p=0.97, 
                                               top_k=150,
                                               temperature=1.0)
            decoded_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=False)[0]
            
            first_sep_id = decoded_output.find(f"{SEP}")
            end_id = decoded_output.find(f"{EOS}")
            response = decoded_output[first_sep_id + 5: end_id].replace("<unk>", "'")

            await message.channel.send(f"@{message.author} {response}")
        


def main():
    secrets = load_secrets()
    username = ...
    
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(secrets["bot_token"])



if (__name__ == "__main__"):
    main() 