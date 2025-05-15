import json, random, textwrap

with open('output/enhanced_test_bank.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

sample = random.sample(questions, 5)

for idx, q in enumerate(sample, 1):
    print(f"\n{idx}. {q['questionText']} (Section: {q['sectionID']}, Difficulty: {q['difficulty']})")
    for choice in q['choices']:
        correct_marker = '*' if choice['isCorrect'] else ' '
        text = textwrap.fill(choice['text'], width=80, subsequent_indent=' ' * 6)
        print(f"   {correct_marker} {choice['label']}. {text}")
    print(f"   Page {q['pageRef']} | Tags: {', '.join(q['tags'])}") 