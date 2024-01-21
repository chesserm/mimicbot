import discord
from transformers import AutoTokenizer, AutoModelForCausalLM

from pre_process_text import process_msg_text
from utils import load_secrets, BOS, SEP, EOS


class MimicBot(discord.Client):
    """
    Created after loosely following Thomas Chaigneau's article: [Building and Launching Your Discord Bot: A Step-by-Step Guide](https://medium.com/@thomaschaigneau.ai/building-and-launching-your-discord-bot-a-step-by-step-guide-f803f7943d33).

    Mixed with this Minimal Bot in [the discordpy docs](https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot).
    """

    def __init__(self, intents : "discord.Intents", username:str, model_prompt:str) -> None:
        """
        Constructor. 

        Input:
            - intents: discord intents object with message content set to True.
            - username: Username of model to load.
        """
        super().__init__(intents=intents)
        self.username = username
        self.model_prompt = model_prompt

        self.tokenizer = AutoTokenizer.from_pretrained(f"models/gpt2/{username}/tokenizer")
        self.model = AutoModelForCausalLM.from_pretrained(f"models/gpt2/{username}/model")
        return 
    

    def __get_model_output(self, message_text:str) -> str:
        """
        Function to get model output from an input string. 

        Input:
            - message_text : The text of the message received.
        
        Output:
            - model_response : The output of the model.
        """

        # Use pre-processing function to ensure same preprocessing as the model was trained on.
        msg_formatted = {"content" : message_text, "mentions" : [] }
        preprocessed_message = process_msg_text(msg_formatted)

        # Format input as the text before the separator token so the model only needs to predict the response
        # NOTE: A ternary is used to add a period at the end of the prompt text. Empirically better performance
        preprocessed_message = f"{BOS} " + preprocessed_message + '.' if preprocessed_message[-1] != '.' else "" +  f" {SEP} "

        # Tokenize preprocessed message and get response. Model params are hard-coded for now.
        inputs = self.tokenizer(preprocessed_message, return_tensors="pt").input_ids
        outputs = self.model.generate(inputs, 
                                    max_new_tokens=200, 
                                    do_sample=True, 
                                    top_p=0.97, 
                                    top_k=150,
                                    temperature=1.0
                                    )
        decoded_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=False)[0]
        
        # We only want the model's response (after SEP token). Including prompt is redundant.
        first_sep_id = decoded_output.find(f"{SEP}")
        end_id = decoded_output.find(f"{EOS}")
        model_response = decoded_output[first_sep_id + len(SEP): end_id].replace("<unk>", "'")

        return model_response


    async def on_ready(self) -> None:
        """
        Ran when bot is alive and connected.

        Input:
            - None 
        
        Output:
            - None (prints to console)
        """
        print(f'Logged on as {self.user}!')
        return 
    

    async def on_message(self, message:"discord.Message") -> None:
        """
        Event Handler for when a message is sent. 
        
        Handles sending of response message as well.

        Input:
            - message: Message object received from discord API through discord library.
        
        Output:
            - None (sends message through discord library functionality)
        """

        if (message.content.startswith(self.model_prompt)):
            # Remove the model prompt of the string.
            message_text = message.content[len(self.model_prompt) : ]

            model_response = self.__get_model_output(message_text)

            await message.channel.send(f"@{message.author} {model_response}")
        


def main():
    secrets = load_secrets()

    # Set the username of the model to load.
    username = ... 

    # Set the prompt token (preceed message to bot with this sequence to get model to read it)
    model_prompt = f"${username}"
    
    intents = discord.Intents.default()
    intents.message_content = True

    client = MimicBot(intents=intents, username=username, model_prompt=model_prompt)
    client.run(secrets["bot_token"])



if (__name__ == "__main__"):
    main() 
