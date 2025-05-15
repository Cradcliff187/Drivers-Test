import os
import json
import random
import argparse

def main():
    parser = argparse.ArgumentParser(description="Preview Enhanced Questions")
    parser.add_argument("--input", default="output/enhanced_test_bank.json", help="Path to enhanced test bank JSON file")
    parser.add_argument("--compare", action="store_true", help="Compare with original test bank")
    parser.add_argument("--num", type=int, default=5, help="Number of questions to preview")
    parser.add_argument("--filter", default=None, help="Filter by section or topic")
    args = parser.parse_args()
    
    # Load enhanced questions
    with open(args.input, "r") as f:
        enhanced_questions = json.load(f)
    
    print(f"\n==== Enhanced Questions Preview ====")
    print(f"Loaded {len(enhanced_questions)} questions from {args.input}")
    
    # Load original questions if comparison requested
    if args.compare:
        original_path = "output/test_bank.json"
        try:
            with open(original_path, "r") as f:
                original_questions = json.load(f)
            print(f"Loaded {len(original_questions)} questions from {original_path} for comparison")
        except FileNotFoundError:
            print("Original questions file not found, comparison disabled")
            args.compare = False
    
    # Apply filter if provided
    filtered_questions = enhanced_questions
    if args.filter:
        filter_term = args.filter.lower()
        filtered_questions = []
        for q in enhanced_questions:
            if (filter_term in q["sectionID"].lower() or 
                filter_term in q["questionText"].lower() or
                any(filter_term in choice["text"].lower() for choice in q["choices"])):
                filtered_questions.append(q)
        print(f"Applied filter '{args.filter}': {len(filtered_questions)} questions match")
    
    # Get random sample of questions
    num_to_show = min(args.num, len(filtered_questions))
    if num_to_show == 0:
        print("No questions match the filter criteria.")
        return
        
    sample_questions = random.sample(filtered_questions, num_to_show)
    
    # Show preview
    for i, q in enumerate(sample_questions):
        print(f"\n{'-'*80}\nQuestion {i+1} of {num_to_show} (ID: {q['questionID']}, Section: {q['sectionID']}, Difficulty: {q['difficulty']})\n")
        
        if args.compare:
            # Find matching original question by ID
            original_q = next((orig_q for orig_q in original_questions if orig_q["questionID"] == q["questionID"]), None)
            
            if original_q:
                print("ORIGINAL QUESTION:")
                print(f"Q: {original_q['questionText']}")
                for choice in original_q["choices"]:
                    indicator = "✓" if choice["isCorrect"] else " "
                    print(f"{indicator} {choice['label']}. {choice['text']}")
                print(f"Explanation: {original_q['explanation']}")
                print("\nENHANCED QUESTION:")
        
        print(f"Q: {q['questionText']}")
        for choice in q["choices"]:
            indicator = "✓" if choice["isCorrect"] else " "
            print(f"{indicator} {choice['label']}. {choice['text']}")
        print(f"Explanation: {q['explanation']}")
        print(f"Page: {q['pageRef']}")
    
    print(f"\n{'-'*80}\n")

if __name__ == "__main__":
    main() 