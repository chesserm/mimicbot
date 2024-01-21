from transformers import OpenAIGPTLMHeadModel, AutoTokenizer
import torch
from torch.utils.data import DataLoader, Dataset
import tqdm
from utils import read_jsonl, BOS, SEP, EOS, PAD, VALID_EMOTES, IMG_TOKEN, GIF_TOKEN, LINK_TOKEN


class MimicDataset(Dataset):
    def __init__(self, train_texts, tokenizer):
        self.raw_strings = train_texts
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.raw_strings)

    def __getitem__(self, idx):
        train_text = self.raw_strings[idx]
        tokenized = self.tokenizer(train_text, return_tensors="pt", padding='max_length', max_length=512, truncation=True)
        input_ids = tokenized.input_ids.squeeze()
        
        # Leaving for reference, but official docs for fine-tuning GPT 2 use same input_ids as label
        # https://huggingface.co/docs/transformers/v4.17.0/en/model_doc/openai-gpt#transformers.OpenAIGPTLMHeadModel
        # labels = torch.full(input_ids.shape, self.tokenizer.pad_token_id)
        # labels[:-1] = input_ids[:-1]
        
        return {
            "input_ids": input_ids,
            # "labels" : labels
        }



def create_tokenizer(model_string : str) -> "AutoTokenizer":
    """
    Helper function to create tokenizer and add any new vocab. 

    Input:
        - model_string: The name of the pretrained model whose tokenizer should be loaded.
    """

    tokenizer = AutoTokenizer.from_pretrained(model_string)

    # https://stackoverflow.com/questions/76198051/how-to-add-new-tokens-to-an-existing-huggingface-tokenizer
    new_vocab = [IMG_TOKEN, GIF_TOKEN, LINK_TOKEN] + VALID_EMOTES
    new_tokens = set(new_vocab) - set(tokenizer.vocab.keys())
    tokenizer.add_tokens(list(new_tokens))

    # We can add these special tokens to the vocabulary and the embeddings of the model:
    tokenizer.add_special_tokens({
        'pad_token': PAD, 
        'sep_token' : SEP, 
        'bos_token' : BOS,
        'eos_token' : EOS
    })

    return tokenizer


def fine_tune(data_loader, model, optimizer, num_epochs, device):
    """
    Fine tunes model using traditional training loop for maximum control.

    Input:
        - data_loader: Data loader
        - model: The model to fine-tune.
        - optimizer: Optimizer for training
        - num_epochs : Number of epochs for training
        - device: Needed for pushing vectors to GPU
    
    Output:
        - model: Fine-tuned model.
    """

    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        for batch in tqdm.tqdm(data_loader):
            input_ids = batch["input_ids"].to(device)
            
            # Forward pass with custom masks
            optimizer.zero_grad()
            outputs = model(input_ids, labels=input_ids)

            loss = outputs.loss
            total_loss += loss.item()

            # Backward pass and optimization
            loss.backward()
            optimizer.step()

        average_loss = total_loss / len(data_loader)
        print(f"Epoch {epoch + 1}/{num_epochs}, Average Loss: {average_loss}")

    return model 



def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    username = ...
    model_string = "openai-gpt"

    # Curate Tokenizer and Dataset.
    tokenizer = create_tokenizer(model_string)

    train_data = [x["train"] for x in read_jsonl(f"../messages/user_messages/{username}.jsonl")]
    user_dataset = MimicDataset(train_data, tokenizer)
    data_loader = DataLoader(user_dataset, batch_size=8, shuffle=True)

    # Define Model
    model = OpenAIGPTLMHeadModel.from_pretrained(model_string)
    model.resize_token_embeddings(len(tokenizer))
    model.to(device)

    # Fine Tuning
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    model = fine_tune(data_loader, model, optimizer, num_epochs=3, device=device)

    # Saving results
    model.save_pretrained(f"models/gpt/{username}/model")
    tokenizer.save_pretrained(f"models/gpt/{username}/tokenizer")

    return 


if (__name__ == "__main__"):
    main()

