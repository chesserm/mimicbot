# MimicBot : A Fine-Tuned Language Model to Mimic User Speech Patterns. 

Scrapes text from a discord channel and uses it to fine-tune a language model from HuggingFace to mimic a user's speech patterns.

All messages scraped with express permission from members of the discord and models were only created for users who gave express permission. Fine-tuned Models are not made public for privacy reasons.

Be very careful not to commit secrets, user messages, or fine-tuned models to avoid leaking information. Take the time to follow the file structure setup described below and update your `.gitignore` as needed. Use at your own risk and don't violate discord ToS or individual's privacy. 

The current setup fine-tunes GPT (GPT 1) using a hacky setup. Futher improvements will explore better models for this use case and more closely follow HuggingFace best practices. 



## Files and Organization

Below is an overview of the main files in the repo:

- `downloader.py` will scrape the messages from a discord channel
- `pre_process_text.py` will preprocess messages into a format for training
- `fine_tune_pre_trained_models/gpt_fine_tune.ipynb` or `fine-tune.py` fine-tunes the model. Both are equivalent, but allow for Jupyter Notebook or Python Script for fine-tuning.
- `frankenstein.py` loads the model and connects to the discord API via the discord package.
- `utils.py` contains helper functions for file loading and writing, but is also were custom tokens are defined for the language model (e.g., end-of-sequence, separator, padding, etc.)

### Custom and Secrets

Any custom information to your project should be placed in the `custom` folder. 

By default, the scripts look for your secrets file in `custom/secrets.json` and is loaded using the helper function in `utils.py`. If you want to change the name or format of your secrets file, just make sure it's appropriately hidden with the `.gitignore` and update the function in `utils.py`. Additionally, you'll want to search the repo for where this function is called, so that you don't get key errors.

Emotes should also be defined one-per-line in `custom/emotes.txt`. For example,

```
:smile:
:joy:
:KEKW:
```

These are loaded at the top of `utils.py`, so simply update that if you format it differently.


### Message Output

Currently, the code writes messages scraped using `downloader.py` to `messages/all_messages.json`.

The `pre_process_text.py` script then takes this JSON and writes individual `.jsonl` files (one per username) to `messages/user_messages/{username}.jsonl`.

### Model Files

Currently, the code writes model files and tokenizers using the following structure: `models/{pretrained_model_name}/{username}/model` and `models/{pretrained_model_name}/{username}/tokenizer`, where:
- `pretrained_model_name` is a string to know what model was fine-tuned (e.g., `"gpt"`)
- `username` is the username of the user the model was trained to mimic.

So, for example, if I wanted to fine-tune the `openai-gpt` model from HuggingFace on a user with username `"matthew"`, then the model files would be saved to `models/gpt/matthew/model` and the tokenizer would be saved to `models/gpt/matthew/tokenizer`. 

**NOTE:** Currently the jupyter-notebook version of the fine-tuning code writes to a model subfolder within the `fine_tune_pre_trained_models` folder. This is intentional to avoid overwriting files, but I may change it in the future so everything is written to the same folder.


## Usage

The following steps will walk through usage of the code in this repo. 

### Step 1: Setting up your secrets file

To use the code as written, you will want to setup your secrets file as follows:

```
{
    "users" : {
        "user1" : {user1_id},
        "user2" : {user2_id},
        ...
    },
    "channels" : {
        "main" : "{channel_id}"
    },
    "headers" : {
        "authorization" : "{authorization_string}"
    },
    "bot_token" : "{bot_token}"
}
```

First, you will want to make sure you have Developer Mode on for discord. To enable this, simply go to your discord settings and navigate to "Advanced" (under App Settings) and set Developer Mode to on.

Then, to get user ID's, you can just right click on a user and copy the user ID from the bottom of the menu.

To get channel ID's, similarly right-click on a channel and copy the Channel ID. **NOTE:** Be careful to grab a channel ID and not a Server ID. 

To get your authorization token for the `headers`, I  recommend following this great 5 minute video from Codium on YouTube called ["Using Python Requests to Retrieve/Scrape Discord Messages (Discord Token)"](https://youtu.be/xh28F6f-Cds), which walks through the process.


Finally, to get a bot_token, you will need to create an application for your bot on the [Discord developer portal](https://discord.com/developers/applications) and get your token from the Bot tab after going through the initial setup (press "Reset Token" to regenerate this). Following [this documentation from discordpy](https://discordpy.readthedocs.io/en/stable/discord.html) is helpful. Make sure to check "message content intent" under the Bot tab as well. 
- NOTE: I only used these fine-tuned bots in a single server. If you plan to deploy this in over 100 servers, you will need to go through the [Discord verification and approval process](https://support.discord.com/hc/en-us/articles/360040720412). 


### Step 2: Setting Up Custom Data

If you want to add custom data (e.g., allow the bot to use a list of emotes in the server), be sure to add them in the `custom` folder. See the above "Files and Organization" Section for more details. 

### Step 3: Dowloading Messages

Edit `downloader.py` to specify the channel to download messages from. This is done by simply verifying or updating the code at the top of the `main()` function, which assumes the channel in `custom/secrets.json` is called `"main"`. 

Once you have this configured, run `downloader.py` to download all messages to `messages/all_messages.json`. 

NOTE: There is rate limiting built-into this code to sleep for 1 second per 100 messages scraped.

### Step 4: Pre-Processing Message Contents

Run `pre_process_text.py` to process all of the messages from step 3 into separate `.jsonl` files for training. 

### Step 5: Fine-Tuning the Model

Fine tune the model by using either `fine_tune_pre_trained_models/gpt_fine_tune.ipynb` or `fine_tune.py` (both are equivalent). You will need to update the `username` variable to tell the code which user's `.jsonl` file to use as training data for the model. 

The code is currently setup for GPT 1 fine-tuning for 3 epochs using the Adam Optimizer. Adjust the model, number of epochs, learning rate, optimizer, etc. as desired before running. 

See the "Files and Organization" section to see where the fine-tuned model and its tokenizer are written.

### Step 6: Connecting the bot and model

Update the `username` variable in `frankenstein.py` to specify which model to use for generating a response to user messages. Then, run the script to bring the bot online. If all is working, you should see the bot "Online" in your discord. 

By default, the prompt that the bot looks for is `${username}`. So, if the model is created to mimic user "matthew", a user would interact with the bot as follows: `$matthew Hello. How are you?`. If a user doesn't use the prefix, the bot won't respond. This prefix can be changed in the `main()` function of `frankenstein.py`.

Currently the code is setup to only use CPU for inference in `frankenstein.py`. 

