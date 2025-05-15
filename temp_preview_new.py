import json
import random

# Load the test bank
with open('output/test_bank.json', 'r') as f:
    data = json.load(f)

# Get specifically the corrected questions
q7 = next(q for q in data if q['questionID'] == 'KDM-00007')  # solid yellow line question
q4 = next(q for q in data if q['questionID'] == 'KDM-00004')  # unlicensed driving penalties
q265 = next(q for q in data if q['questionID'] == 'KDM-00265')  # airbag safety

# Get 2 other random questions (not the ones we just fixed)
others = [q for q in data if q['questionID'] not in ['KDM-00007', 'KDM-00004', 'KDM-00265']]
random.seed(42)
selected = random.sample(others, 2)

# Combine all questions in a new list and shuffle them
preview = [q7, q4, q265] + selected
random.shuffle(preview)

# Print the questions in the requested format
for i, q in enumerate(preview, 1):
    print("Q" + str(i) + " (" + q['difficulty'] + ") – " + q['questionText'])
    for c in q['choices']:
        mark = '✅' if c['isCorrect'] else ''
        print(c['label'] + ". " + c['text'] + " " + mark)
    tag = q['tags'][0] if q['tags'] else ''
    print("Pg " + str(q['pageRef']) + " • Tags: " + tag)
    print() 