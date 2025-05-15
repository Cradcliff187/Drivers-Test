import json
import random

# Load the test bank
with open('output/test_bank.json', 'r') as f:
    data = json.load(f)

# Get the accident question that was edited
q11 = next(q for q in data if q['questionID'] == 'KDM-00011')

# Get 4 other random questions
others = [q for q in data if q['questionID'] != 'KDM-00011']
random.seed(123)
random_selection = random.sample(others, 4)

preview = [q11] + random_selection
random.shuffle(preview)

# Print the questions in the requested format
for i, q in enumerate(preview, 1):
    # Split long question text to avoid wrapping issues
    question_text = q['questionText']
    print(f"Q{i} ({q['difficulty']}) – {question_text}")
    
    for c in q['choices']:
        mark = '✅' if c['isCorrect'] else ''
        choice_text = c['text']
        print(f"{c['label']}. {choice_text} {mark}")
    
    tag = q['tags'][0] if q['tags'] else ''
    print(f"Pg {q['pageRef']} • Tags: {tag}")
    print() 