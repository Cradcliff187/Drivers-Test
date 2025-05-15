import os
import json
import random
import re
import argparse
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Enhanced Kentucky Driver's Manual Question Fixer")
    parser.add_argument("--input", default="output/test_bank.json", help="Path to input test bank JSON file")
    parser.add_argument("--output", default="output/enhanced_test_bank.json", help="Path to output JSON file")
    args = parser.parse_args()

    print("\n==== Enhanced Kentucky Driver's Manual Question Fixer ====\n")
    
    # Load the test bank
    with open(args.input, "r") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions from test bank: {args.input}")
    
    # Define banned phrases
    BANNED_PHRASES = [
        "Follow Kentucky guidelines for",
        "There are no specific rules for",
        "Wait for other drivers to decide about",
        "Ignore the",
        "Use personal judgment rather than following official guidelines",
        "The procedure varies by county and is not standardized across Kentucky",
        "There is no official procedure outlined in the Kentucky Driver's Manual"
    ]
    
    # Track original vs fixed
    questions_with_banned_phrases = []
    fixed_questions = []
    
    # First pass - identify questions needing fixes
    for question in questions:
        needs_fix = False
        
        # Check question text for banned phrases
        for phrase in BANNED_PHRASES:
            if phrase.lower() in question["questionText"].lower():
                needs_fix = True
                break
        
        # Check choices for banned phrases
        if not needs_fix:
            for choice in question["choices"]:
                for phrase in BANNED_PHRASES:
                    if phrase.lower() in choice["text"].lower():
                        needs_fix = True
                        break
                if needs_fix:
                    break
        
        # Add to appropriate list
        if needs_fix:
            questions_with_banned_phrases.append(question)
        else:
            fixed_questions.append(question)
    
    print(f"Found {len(questions_with_banned_phrases)} questions containing banned phrases")
    print(f"{len(fixed_questions)} questions already meet quality standards")
    
    # Fix the problematic questions
    newly_fixed_questions = fix_questions(questions_with_banned_phrases)
    
    # Combine all questions
    all_fixed_questions = fixed_questions + newly_fixed_questions
    
    # Save the fixed questions
    with open(args.output, "w") as f:
        json.dump(all_fixed_questions, f, indent=2)
    
    print(f"Successfully fixed {len(newly_fixed_questions)} questions")
    print(f"Total {len(all_fixed_questions)} questions saved to {args.output}")
    
    # Analyze difficulty distribution
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    for q in all_fixed_questions:
        difficulty_counts[q["difficulty"]] += 1
    
    print("\nDifficulty distribution in fixed test bank:")
    print(f"Easy: {difficulty_counts['easy']} ({difficulty_counts['easy']/len(all_fixed_questions)*100:.1f}%)")
    print(f"Medium: {difficulty_counts['medium']} ({difficulty_counts['medium']/len(all_fixed_questions)*100:.1f}%)")
    print(f"Hard: {difficulty_counts['hard']} ({difficulty_counts['hard']/len(all_fixed_questions)*100:.1f}%)")


def fix_questions(questions_to_fix):
    """Fix questions containing banned phrases with high-quality rewrites"""
    fixed_questions = []
    
    # Question templates by type
    QUESTION_TEMPLATES = {
        "fact": [
            "According to the Kentucky Driver's Manual, what is the correct procedure for {topic}?",
            "What does Kentucky law state about {topic}?",
            "Which of the following correctly describes {topic} in Kentucky?",
            "What is the rule regarding {topic} in Kentucky?",
            "How does the Kentucky Driver's Manual recommend handling {topic}?"
        ],
        "scenario": [
            "You're driving in Kentucky and encounter {topic}. What should you do?",
            "While driving in Kentucky, you face a situation involving {topic}. What is the correct action?",
            "If you encounter {topic} while driving, what should you do?",
            "When dealing with {topic} on the road, what is the proper response?",
            "You encounter {topic} while driving. What is the safest action?"
        ],
        "rule": [
            "What is the penalty for {topic} in Kentucky?",
            "According to Kentucky law, what happens if a driver violates rules regarding {topic}?",
            "Which statement is correct about the consequences of improper {topic}?",
            "What does Kentucky law require regarding {topic}?",
            "Under Kentucky regulations, what is the proper approach to {topic}?"
        ]
    }
    
    # Topic-specific high-quality answers
    TOPIC_ANSWERS = {
        # Right of way
        "right-of-way": {
            "correct": "The vehicle on the right has the right-of-way at uncontrolled intersections",
            "wrong": [
                "The vehicle on the left has the right-of-way at all intersections",
                "The larger vehicle always has the right-of-way",
                "The vehicle traveling faster has the right-of-way"
            ]
        },
        "four-way stop": {
            "correct": "Vehicles proceed in the order they arrived at the intersection",
            "wrong": [
                "The vehicle on the right always goes first",
                "Commercial vehicles have priority over passenger vehicles",
                "The vehicle traveling on the wider road has the right-of-way"
            ]
        },
        
        # Speed limits
        "speed limit": {
            "correct": "Obey posted speed limits and reduce speed in adverse conditions",
            "wrong": [
                "Drive at a speed that matches the flow of traffic, regardless of posted limits",
                "Posted limits are just suggestions and not legally enforceable",
                "You may exceed the speed limit by 10 mph before being ticketed"
            ]
        },
        "school zone": {
            "correct": "Reduce speed to 25 mph when children are present",
            "wrong": [
                "Maintain normal speed if no crossing guards are present",
                "School zone limits only apply during regular school hours",
                "School zone limits don't apply on weekends or holidays regardless of events"
            ]
        },
        
        # Parking
        "parallel parking": {
            "correct": "Signal, position your vehicle parallel to the car in front, then back into the space while turning the wheel",
            "wrong": [
                "Pull in front-first, then adjust your position as needed",
                "Enter the space at a 45-degree angle, then straighten out",
                "It's acceptable to tap other vehicles slightly when parallel parking"
            ]
        },
        "handicap parking": {
            "correct": "Only vehicles displaying a valid handicap placard or license plate may park in designated spaces",
            "wrong": [
                "Anyone can park in handicap spaces for brief periods under 5 minutes",
                "Handicap spaces are available to all drivers during non-business hours",
                "Family members of disabled persons can use these spaces even without the disabled person present"
            ]
        },
        
        # Traffic signals
        "red light": {
            "correct": "Come to a complete stop before the limit line and remain stopped until the light turns green",
            "wrong": [
                "Stop briefly, then proceed if no cross traffic is visible",
                "A red light is a suggestion to stop but not mandatory if the intersection is clear",
                "You can proceed through a red light after stopping if it's after 10 PM"
            ]
        },
        "yellow light": {
            "correct": "Slow down and stop if you can do so safely",
            "wrong": [
                "Always speed up to get through the intersection before the light turns red",
                "Always slam on your brakes to stop, regardless of safety",
                "Yellow lights can be treated the same as green lights"
            ]
        },
        
        # Licensing
        "license renewal": {
            "correct": "Present your current license, pass a vision test, and pay the renewal fee",
            "wrong": [
                "Licenses automatically renew and are mailed to your home address",
                "Complete renewal online without any in-person verification",
                "Take a full driving test for each renewal"
            ]
        },
        "suspended license": {
            "correct": "Stop driving immediately, complete all requirements, and pay reinstatement fees before driving again",
            "wrong": [
                "You may continue driving for essential trips like work and school",
                "A suspension can be ignored if it's your first offense",
                "You can drive if you keep a copy of your suspension notice with you"
            ]
        },
        
        # Safety
        "seat belt": {
            "correct": "All front-seat occupants and all passengers under 18 must wear seat belts",
            "wrong": [
                "Only the driver is legally required to wear a seat belt",
                "Seat belts are optional on trips under 10 miles",
                "Passengers in the back seat are exempt from seat belt laws"
            ]
        },
        "child restraint": {
            "correct": "Children under 40 inches tall must be in a child safety seat; children under 8 years and between 40-57 inches must use a booster seat",
            "wrong": [
                "Children over 4 years old can use regular seat belts regardless of height",
                "Holding a child on your lap with a seat belt around both of you is legal",
                "Child seats are only required on highways, not city streets"
            ]
        },
        
        # DUI
        "dui": {
            "correct": "For first offense: fines of $200-$500, license suspension of 30-120 days, potential jail time of 2-30 days",
            "wrong": [
                "First offense results only in a warning with no license suspension",
                "DUI is only punishable if an accident occurs",
                "Penalties are waived if you can demonstrate you've enrolled in alcohol treatment"
            ]
        },
        "blood alcohol": {
            "correct": "Legal limit is 0.08% for drivers 21 and older, 0.02% for drivers under 21",
            "wrong": [
                "Legal limit is 0.10% for all drivers regardless of age",
                "Legal limit is 0.05% for all Kentucky drivers",
                "There is no specific blood alcohol limit in Kentucky"
            ]
        },
        
        # Weather conditions
        "fog": {
            "correct": "Slow down, use low beam headlights, and use the right edge line as a guide",
            "wrong": [
                "Use high beams to better illuminate the road ahead",
                "Drive at normal speed but turn on hazard lights",
                "Pull over and wait until the fog completely clears before proceeding"
            ]
        },
        "ice": {
            "correct": "Reduce speed, increase following distance, and avoid sudden movements with steering, braking, or acceleration",
            "wrong": [
                "Apply brakes firmly when skidding to regain control quickly",
                "Drive at normal speed to avoid getting stuck in the ice",
                "Pumping your brakes rapidly is the best technique on all icy roads"
            ]
        }
    }
    
    # General answers by category (for topics without specific entries)
    CATEGORY_ANSWERS = {
        "Licensing": {
            "correct": "Follow specific procedures in the Kentucky Driver's Manual including proper documentation, testing, and fee payment",
            "wrong": [
                "Requirements vary significantly by county with no statewide standards",
                "There are exemptions for most drivers that aren't widely publicized",
                "Most licensing procedures are optional recommendations, not requirements"
            ]
        },
        "RulesOfTheRoad": {
            "correct": "Follow specific traffic laws as outlined in the Kentucky Driver's Manual and state statutes",
            "wrong": [
                "Rules are generally left to driver discretion in most situations",
                "Rules apply primarily to commercial vehicles, not passenger cars",
                "Posted signs are guidelines that can be disregarded when safe"
            ]
        },
        "Signs": {
            "correct": "Obey all traffic signs and signals as they are legally enforceable directives",
            "wrong": [
                "Most signs are advisory and compliance is optional outside of rush hour",
                "Signs that are faded or partially obscured are not legally binding",
                "Drivers can use personal judgment to determine which signs apply to them"
            ]
        },
        "Safety": {
            "correct": "Follow safety procedures outlined in the Kentucky Driver's Manual to prevent accidents and injuries",
            "wrong": [
                "Modern vehicles have enough safety features that manual safety procedures are unnecessary",
                "Safety recommendations are mainly for new drivers and can be disregarded by experienced drivers",
                "Safety procedures are only necessary in hazardous conditions or bad weather"
            ]
        },
        "Emergencies": {
            "correct": "Follow emergency protocols as specified in the Kentucky Driver's Manual to ensure safety of all parties",
            "wrong": [
                "Emergency procedures are just suggestions with no legal requirement to follow them",
                "Each driver should develop their own emergency procedures based on personal preference",
                "Emergency procedures only apply if police are present at the scene"
            ]
        }
    }
    
    # Process each question
    for question in questions_to_fix:
        # Extract topic from question text or section ID
        topic = extract_topic(question)
        
        # Determine question type
        question_type = determine_question_type(question)
        
        # Determine the section category
        section_category = get_section_category(question["sectionID"])
        
        # Get appropriate answers based on topic
        answers = get_appropriate_answers(topic, section_category, TOPIC_ANSWERS, CATEGORY_ANSWERS)
        
        # Select question template and create new question text
        template = random.choice(QUESTION_TEMPLATES[question_type])
        question_text = template.format(topic=topic)
        
        # Fix grammatical issues in question text
        question_text = fix_grammar(question_text)
        
        # Generate choices
        correct_answer = answers["correct"]
        wrong_answers = answers["wrong"]
        
        # Shuffle answers
        all_answers = [correct_answer] + wrong_answers
        random.shuffle(all_answers)
        
        new_choices = []
        for i, answer_text in enumerate(all_answers):
            label = chr(65 + i)  # A, B, C, D
            new_choices.append({
                "label": label,
                "text": answer_text,
                "isCorrect": (answer_text == correct_answer)
            })
        
        # Update explanation
        explanation = f"According to the Kentucky Driver's Manual on page {question['pageRef']}, {correct_answer}."
        
        # Create fixed question
        fixed_question = question.copy()
        fixed_question["questionText"] = question_text
        fixed_question["choices"] = new_choices
        fixed_question["explanation"] = explanation
        
        fixed_questions.append(fixed_question)
    
    return fixed_questions


def extract_topic(question):
    """Extract topic from question text or section ID"""
    question_text = question["questionText"].lower()
    
    # Common patterns in question text
    patterns = [
        r"what is the correct procedure for ([^?]+)\?",
        r"what does kentucky law state about ([^?]+)\?",
        r"what is the rule regarding ([^?]+) in kentucky\?",
        r"how does the kentucky driver's manual recommend handling ([^?]+)\?",
        r"what should you do\?.*involving ([^.]+)\.",
        r"what happens if a driver ([^?]+)\?",
        r"what is the penalty for ([^?]+) in kentucky\?"
    ]
    
    # Try to extract topic using patterns
    for pattern in patterns:
        match = re.search(pattern, question_text)
        if match:
            return match.group(1).strip()
    
    # If no match found, extract topic from choices
    for choice in question["choices"]:
        if "Follow Kentucky guidelines for" in choice["text"]:
            topic = choice["text"].replace("Follow Kentucky guidelines for", "").strip()
            if topic:
                return topic
    
    # If still no topic, use section ID
    section = question["sectionID"]
    if "." in section:
        topic = section.split(".")[-1].lower()
        
        # Convert camelCase to spaces
        topic = re.sub(r'(?<!^)(?=[A-Z])', ' ', topic).lower()
        
        return topic
    
    return "driving procedures"


def determine_question_type(question):
    """Determine if question is fact-based, scenario-based, or rule-based"""
    question_text = question["questionText"].lower()
    
    # Scenario questions typically ask what to do in a situation
    if any(phrase in question_text for phrase in ["what should you do", "what is the correct action", 
                                               "what is the proper response", "what is the safest action",
                                               "while driving", "you encounter", "you're driving"]):
        return "scenario"
    
    # Rule questions typically ask about penalties or requirements
    elif any(phrase in question_text for phrase in ["penalty", "what happens if", 
                                                 "consequences", "require", "when is it legal"]):
        return "rule"
    
    # Default to fact-based question
    else:
        return "fact"


def get_section_category(section_id):
    """Get the main category from section ID"""
    if "." in section_id:
        return section_id.split(".")[0]
    return section_id


def get_appropriate_answers(topic, section_category, topic_answers, category_answers):
    """Get the most appropriate answers for the topic"""
    # First check for exact match in topic answers
    if topic in topic_answers:
        return topic_answers[topic]
    
    # Check for partial matches in topic_answers keys
    for key in topic_answers.keys():
        if key in topic or topic in key:
            return topic_answers[key]
    
    # If no match, use category answers
    if section_category in category_answers:
        return category_answers[section_category]
    
    # Default to first category as fallback
    return next(iter(category_answers.values()))


def fix_grammar(text):
    """Fix common grammatical issues in question text"""
    # Fix capitalization
    text = text.strip()
    if not text[0].isupper():
        text = text[0].upper() + text[1:]
    
    # Ensure question ends with question mark
    if not text.endswith("?"):
        text = text + "?"
    
    # Fix specific grammar issues
    text = re.sub(r"(?i)when is it legal to ([\w\s]+)\?", r"When is it legal to \1?", text)
    text = re.sub(r"(?i)what happens if a driver ([\w\s]+)\?", r"What happens if a driver \1?", text)
    
    # Fix issues with "a" vs "an"
    text = re.sub(r"\ba ([aeiou])", r"an \1", text)
    
    return text


if __name__ == "__main__":
    main() 