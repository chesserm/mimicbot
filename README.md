# MimicBot

## A Fine-Tuned Language Model to Mimic User Speech Patterns

Scrapes text from a discord channel and uses it to fine-tune a language model from HuggingFace to mimic a user's speech patterns. All messages scraped with permission and models only created for users with express permission. Fine-tuned Models are not made public for privacy reasons. 

The current setup fine-tunes GPT-2 using a hacky setup. Futher improvements will explore better models for this use case and better data preprocessing methods. 

**There is lots of work still to do (including lots of documentation and cleanup), but it is in a functional state as-is.**

## Usage

- `downloader.py` will scrape the messages from a discord channel
- `pre_process_text.py` will  preprocess those into a format for training
- `fine_tune_pre_trained_models/gpt2_fine_tune.ipynb` fine-tunes the model 
- `frankenstein.py` loads the model and connects to the discord API via the discord package.

Much more documenation and cleanup coming. Use at your own risk and don't violate discord ToS or individual's privacy. 

# BE CAREFUL NOT TO COMMIT SECRETS, PERSONAL INFORMATION, OR USER DATA TO YOUR REPO.



