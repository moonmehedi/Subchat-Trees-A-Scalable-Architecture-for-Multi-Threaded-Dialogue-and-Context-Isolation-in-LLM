# Step 1: Install Hugging Face datasets if not already
# pip install datasets

from datasets import load_dataset

# Step 2: Load the QASPER dataset
dataset = load_dataset("allenai/qasper")

# Step 3: Convert each split (train/validation/test) to JSON
# Hugging Face datasets have multiple splits, so you can save them separately

# Save the training set
dataset["train"].to_json("qasper_train.json")

# Save the validation set
dataset["validation"].to_json("qasper_validation.json")

# Save the test set
dataset["test"].to_json("qasper_test.json")
