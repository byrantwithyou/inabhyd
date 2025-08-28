import pickle
import sys
with open(sys.argv[1], "rb") as file:
    replies = pickle.load(file)
print(replies)