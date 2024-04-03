import random


# Define the number of words
num_words = 500000
all_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
# Open a file for writing in text mode
with open("files/500K.txt", "w") as f:
    # Loop to write each word on a separate line
    for _ in range(num_words):
        random_string = ''.join(random.sample(all_chars, 8))
        f.write(f"{random_string}\n")

print(f"File '500K.txt' created with {num_words} words.")
