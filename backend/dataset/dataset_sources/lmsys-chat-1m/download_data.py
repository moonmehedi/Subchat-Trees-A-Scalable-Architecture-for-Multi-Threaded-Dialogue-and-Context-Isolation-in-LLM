from datasets import load_dataset

# Load the dataset
dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")

# Apply your filter: turn >= 20
filtered_dataset = dataset.filter(lambda x: x["turn"] >= 20)

# Count the filtered rows
print("Total conversations with turn >= 20:", len(filtered_dataset))

# Save locally if needed
filtered_dataset.to_json("filtered_conversations.json")
