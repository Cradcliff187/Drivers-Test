import random
import re
from typing import List, Dict, Any
import numpy as np
from pydantic import BaseModel
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class QuestionChoice(BaseModel):
    label: str
    text: str
    isCorrect: bool = False

class Question(BaseModel):
    questionID: str
    sectionID: str
    difficulty: str
    questionText: str
    choices: List[QuestionChoice]
    explanation: str
    pageRef: int
    tags: List[str]
    requiresImage: bool = False
    imagePrompt: str = None

class ChunkWithEmbedding(BaseModel):
    id: str
    text: str
    section: str
    pageNum: int
    embedding: List[float]

class QuestionGenerator:
    """
    Generates test questions from the Kentucky Driver's Manual content
    using semantic similarity and structured content analysis
    """
    
    def __init__(self, sections, chunks, model_name='all-MiniLM-L6-v2'):
        self.sections = sections
        self.chunks = chunks
        self.section_map = {s['id']: s for s in sections}
        
        # Initialize embedding model
        self.model = SentenceTransformer(model_name)
        self.embed_chunks()
        
        # Define question templates
        self.templates = self._initialize_templates()
        
        # Tag categories for questions
        self.tag_categories = {
            "signs": ["road sign", "traffic sign", "warning sign", "regulatory sign", "yield", "stop sign"],
            "signals": ["traffic signal", "traffic light", "flashing", "yellow light", "red light", "green light"],
            "speed": ["speed limit", "mph", "speeding", "minimum speed", "maximum speed", "too fast"],
            "parking": ["parking", "parallel park", "handicap parking", "no parking", "fire hydrant"],
            "safetyDevices": ["seat belt", "child restraint", "airbag", "helmet", "safety device"],
            "licensing": ["license", "permit", "driver license", "commercial", "cdl", "suspension", "revocation"],
            "alcohol": ["dui", "dwi", "alcohol", "drunk driving", "blood alcohol", "bac", "impaired"],
            "motorcycles": ["motorcycle", "moped", "helmet", "passenger", "lane splitting"],
            "weather": ["fog", "rain", "snow", "ice", "slick", "visibility", "storm", "hazardous weather"]
        }
    
    def _initialize_templates(self):
        """Initialize various question templates for different types of questions"""
        templates = {
            "fact": [
                "According to the Kentucky Driver's Manual, what is the {topic}?",
                "What does the Kentucky Driver's Manual state about {topic}?",
                "Which of the following correctly describes {topic}?",
                "What is the rule regarding {topic} in Kentucky?",
                "How does the Kentucky Driver's Manual define {topic}?"
            ],
            "scenario": [
                "You are driving and {scenario}. What should you do?",
                "While driving in Kentucky, {scenario}. What is the correct action?",
                "If {scenario} occurs while driving, you should:",
                "When {scenario}, the proper response is to:",
                "You encounter {scenario} on the road. What is the safest action?"
            ],
            "rule": [
                "What is the penalty for {violation} in Kentucky?",
                "According to Kentucky law, what happens if a driver {violation}?",
                "Which statement is correct about the consequences of {violation}?",
                "What does Kentucky law require regarding {requirement}?",
                "Under Kentucky regulations, when is it legal to {action}?"
            ],
            "calculation": [
                "If {scenario}, calculate {calculation_target}.",
                "What is {calculation_target} when {scenario}?",
                "Calculate {calculation_target} in the following situation: {scenario}",
                "Based on the Kentucky Driver's Manual, what is {calculation_target} if {scenario}?"
            ],
            "sign": [
                "What does this road sign indicate? [REQUIRES IMAGE]",
                "Which of the following best describes the meaning of this traffic sign? [REQUIRES IMAGE]",
                "When you see this sign, you should: [REQUIRES IMAGE]",
                "This road sign warns drivers about: [REQUIRES IMAGE]"
            ]
        }
        return templates
    
    def embed_chunks(self):
        """Create embeddings for all text chunks"""
        print("Creating embeddings for text chunks...")
        for i, chunk in enumerate(tqdm(self.chunks)):
            if not hasattr(chunk, 'embedding') or chunk.embedding is None:
                text_embedding = self.model.encode(chunk['text'])
                self.chunks[i]['embedding'] = text_embedding.tolist()
    
    def find_most_similar_chunks(self, query, n=3):
        """Find chunks most similar to the query using semantic search"""
        query_embedding = self.model.encode(query)
        
        similarities = []
        for chunk in self.chunks:
            chunk_embedding = np.array(chunk['embedding'])
            similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][0]
            similarities.append((chunk, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top n results
        return [item[0] for item in similarities[:n]]
    
    def extract_fact_from_chunk(self, chunk, topic):
        """Extract a fact related to the topic from a chunk"""
        # Simple approach: find sentences containing the topic
        sentences = re.split(r'[.!?]', chunk['text'])
        relevant_sentences = [s for s in sentences if topic.lower() in s.lower()]
        
        if relevant_sentences:
            return relevant_sentences[0].strip()
        else:
            return chunk['text'][:200]  # Just take the first part if nothing specific found
    
    def generate_wrong_answers(self, correct_answer, topic, num_wrong=3):
        """Generate plausible wrong answers"""
        wrong_answers = []
        
        # Strategy 1: Find related chunks and extract information
        related_chunks = self.find_most_similar_chunks(topic, n=5)
        
        for chunk in related_chunks:
            fact = self.extract_fact_from_chunk(chunk, topic)
            # Ensure it's different from correct answer
            if fact and fact != correct_answer and len(fact) < 150:
                wrong_answers.append(fact)
                if len(wrong_answers) >= num_wrong:
                    break
        
        # Strategy 2: Modify the correct answer if we need more wrong answers
        while len(wrong_answers) < num_wrong:
            if not correct_answer:
                wrong_answers.append(f"Option not mentioned in the manual")
            else:
                # Simple modifications - in a real implementation, these would be more sophisticated
                negations = ["not", "never", "isn't", "doesn't", "won't"]
                modifiers = ["always", "only", "sometimes", "rarely", "frequently", "never"]
                
                if any(neg in correct_answer.lower() for neg in negations):
                    # Remove negation
                    for neg in negations:
                        if neg in correct_answer.lower():
                            wrong_answers.append(correct_answer.replace(neg, ""))
                            break
                else:
                    # Add negation
                    words = correct_answer.split()
                    if len(words) > 3:
                        insert_pos = min(len(words) // 3, 2)  # Insert near the beginning
                        words.insert(insert_pos, random.choice(negations))
                        wrong_answers.append(" ".join(words))
                
                # Change numbers if present
                numbers = re.findall(r'\d+', correct_answer)
                if numbers:
                    for num in numbers:
                        # Adjust number up or down
                        new_num = int(num) + random.choice([-2, -1, 1, 2, 5, 10])
                        if new_num <= 0:
                            new_num = int(num) + random.choice([1, 2, 5, 10])
                        wrong_answer = correct_answer.replace(num, str(new_num))
                        wrong_answers.append(wrong_answer)
                        break
        
        # Ensure we have exactly num_wrong answers
        return wrong_answers[:num_wrong]
    
    def determine_question_tags(self, question_text, section_id):
        """Determine appropriate tags for a question"""
        tags = []
        section = self.section_map.get(section_id, {})
        
        # Add tag based on section if possible
        section_title = section.get('title', '').lower()
        for tag, keywords in self.tag_categories.items():
            # Check if any keyword appears in the section title or question
            if any(keyword in section_title for keyword in keywords):
                tags.append(tag)
                break
            if any(keyword in question_text.lower() for keyword in keywords):
                tags.append(tag)
                break
        
        # If no tags found based on content, add a default tag
        if not tags:
            tags.append(random.choice(list(self.tag_categories.keys())))
        
        # Add 1-2 more random tags
        available_tags = [t for t in self.tag_categories.keys() if t not in tags]
        num_extra = min(len(available_tags), random.randint(0, 2))
        if num_extra > 0:
            extra_tags = random.sample(available_tags, num_extra)
            tags.extend(extra_tags)
        
        return tags
    
    def create_question_from_chunk(self, chunk, question_id, difficulty='easy'):
        """Create a question from a text chunk"""
        section_id = chunk['section']
        section = self.section_map.get(section_id, {})
        
        # Identify potential topics in the chunk
        text = chunk['text']
        sentences = re.split(r'[.!?]', text)
        
        # Filter out very short sentences and get one for our question
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 30 and len(s.strip()) < 150]
        if not valid_sentences:
            valid_sentences = [text[:150]] if text else ["Kentucky driving rules"]
        
        topic_sentence = random.choice(valid_sentences)
        
        # Determine question type based on content
        has_numbers = bool(re.search(r'\d+', topic_sentence))
        
        if "sign" in section.get('title', '').lower() and random.random() < 0.7:
            question_type = "sign"
            requires_image = True
        elif has_numbers and random.random() < 0.3:
            question_type = "calculation"
            requires_image = False
        elif "penalty" in topic_sentence.lower() or "fine" in topic_sentence.lower():
            question_type = "rule"
            requires_image = False
        elif random.random() < 0.4:
            question_type = "scenario"
            requires_image = random.random() < 0.1  # 10% chance of scenario with image
        else:
            question_type = "fact"
            requires_image = False
        
        # Extract topic or scenario from the sentence
        words = topic_sentence.split()
        if len(words) > 8:
            # Get a meaningful part of the sentence
            topic_words = words[:min(8, len(words) // 2)]
            topic = " ".join(topic_words)
        else:
            topic = topic_sentence
            
        # Format question according to type
        templates = self.templates.get(question_type, self.templates["fact"])
        question_template = random.choice(templates)
        
        if question_type == "fact":
            question_text = question_template.format(topic=topic)
        elif question_type == "scenario":
            scenario = topic_sentence
            question_text = question_template.format(scenario=scenario)
        elif question_type == "rule":
            if "penalty" in topic_sentence.lower() or "fine" in topic_sentence.lower():
                violation = re.sub(r'penalty|fine|punish\w*', '', topic_sentence, flags=re.IGNORECASE).strip()
                question_text = question_template.format(violation=violation)
            else:
                question_text = question_template.format(
                    violation=topic, 
                    requirement=topic,
                    action=topic
                )
        elif question_type == "calculation":
            scenario = topic_sentence
            calculation_targets = ["the stopping distance", "the reaction time", "the total braking distance", 
                                "the speed limit", "the blood alcohol content (BAC)"]
            question_text = question_template.format(
                scenario=scenario,
                calculation_target=random.choice(calculation_targets)
            )
        elif question_type == "sign":
            question_text = random.choice(templates)
        
        # Create correct answer
        correct_answer = self.extract_fact_from_chunk(chunk, topic)
        
        # Generate wrong answers
        wrong_answers = self.generate_wrong_answers(correct_answer, topic)
        
        # Create choices
        all_answers = [correct_answer] + wrong_answers
        random.shuffle(all_answers)
        
        choices = []
        for i, answer in enumerate(all_answers):
            choices.append(QuestionChoice(
                label=chr(65 + i),  # A, B, C, D
                text=answer,
                isCorrect=(answer == correct_answer)
            ))
        
        # Determine tags
        tags = self.determine_question_tags(question_text, section_id)
        
        # Create image prompt if needed
        image_prompt = None
        if requires_image:
            if question_type == "sign":
                sign_types = ["STOP sign", "YIELD sign", "Speed Limit sign", "School Zone sign", 
                             "No Left Turn sign", "Railroad Crossing sign", "Merge sign",
                             "Do Not Enter sign", "Wrong Way sign", "No U-Turn sign"]
                image_prompt = f"An image of a {random.choice(sign_types)}"
            else:
                scenarios = ["wet road conditions", "proper following distance", 
                            "parallel parking procedure", "blind spot check",
                            "proper lane change", "highway merging", "school bus stopping"]
                image_prompt = f"An image showing {random.choice(scenarios)}"
        
        # Create question
        question = Question(
            questionID=f"KDM-{question_id:05d}",
            sectionID=section_id,
            difficulty=difficulty,
            questionText=question_text,
            choices=choices,
            explanation=f"According to the Kentucky Driver's Manual on page {chunk['pageNum']}, {correct_answer}",
            pageRef=chunk['pageNum'],
            tags=tags,
            requiresImage=requires_image,
            imagePrompt=image_prompt if requires_image else None
        )
        
        return question
    
    def generate_test_bank(self, num_questions=400):
        """Generate the full test bank of questions"""
        questions = []
        question_id = 1
        
        # Define target distribution of difficulties
        # 50% easy, 35% medium, 15% hard
        difficulty_targets = {
            "easy": int(num_questions * 0.5),
            "medium": int(num_questions * 0.35),
            "hard": int(num_questions * 0.15)
        }
        
        # Ensure the total adds up to num_questions
        total = sum(difficulty_targets.values())
        if total < num_questions:
            difficulty_targets["easy"] += (num_questions - total)
        
        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        
        # First pass: Generate at least the minimum questions per section
        print("Generating questions...")
        
        # Track chunks used to avoid repetition
        chunks_used = set()
        
        # Ensure at least 8 questions per top-level chapter and 1 per subsection
        for section in tqdm(self.sections):
            level = section.get('level', 1)
            min_questions = 8 if level == 1 else 1
            
            # Find chunks for this section
            section_chunks = [c for c in self.chunks if c['section'] == section['id']]
            if not section_chunks:
                continue
                
            # Generate questions for this section
            for _ in range(min_questions):
                # Try to find a chunk we haven't used yet
                available_chunks = [c for c in section_chunks if c['id'] not in chunks_used]
                if not available_chunks:
                    available_chunks = section_chunks  # Reuse if necessary
                
                chunk = random.choice(available_chunks)
                chunks_used.add(chunk['id'])
                
                # Determine difficulty based on targets and current counts
                remaining_difficulties = [d for d, count in difficulty_counts.items() 
                                       if count < difficulty_targets[d]]
                
                if not remaining_difficulties:  # If we've met all targets, default to easy
                    difficulty = "easy"
                else:
                    difficulty = random.choice(remaining_difficulties)
                
                # Create the question
                question = self.create_question_from_chunk(chunk, question_id, difficulty)
                questions.append(question)
                question_id += 1
                
                # Update difficulty count
                difficulty_counts[difficulty] += 1
        
        # Second pass: Fill up to the target number of questions
        while len(questions) < num_questions:
            # Select a random chunk
            chunk = random.choice(self.chunks)
            
            # Determine difficulty based on remaining targets
            remaining_difficulties = [d for d, count in difficulty_counts.items() 
                                   if count < difficulty_targets[d]]
            
            if not remaining_difficulties:  # If we've met all targets, pick randomly based on desired distribution
                difficulty = random.choices(
                    ["easy", "medium", "hard"],
                    weights=[0.5, 0.35, 0.15],
                    k=1
                )[0]
            else:
                difficulty = random.choice(remaining_difficulties)
            
            # Create the question
            question = self.create_question_from_chunk(chunk, question_id, difficulty)
            questions.append(question)
            question_id += 1
            
            # Update difficulty count
            difficulty_counts[difficulty] += 1
        
        return questions 