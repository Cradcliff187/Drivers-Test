# Kentucky Driver's Manual Test-Bank Generator

A comprehensive tool for generating test questions based on the Kentucky Driver's Manual.

Updated: May 15, 2025

This project processes the Kentucky State Driver's Manual PDF and generates a comprehensive test bank of multiple-choice questions. The questions can be used for study purposes or integrated into a testing application.

## Features

- Extracts and processes the entire Kentucky Driver's Manual PDF
- Generates 400+ multiple-choice questions across all sections
- Creates questions with varied difficulty levels: easy (50%), medium (35%), and hard (15%)
- Includes scenario-based, fact-based, calculation, and image-requiring questions
- Properly tagged questions for easy filtering and categorization
- Comprehensive coverage across all manual sections
- Outputs in JSON format for easy integration with front-end applications

## Requirements

- Python 3.8+
- Required Python packages (install via `pip install -r requirements-dev.txt`):
  - pypdf
  - pytesseract
  - Pillow
  - numpy
  - scikit-learn
  - sentence-transformers
  - pydantic
  - tqdm
  - PyMuPDF

### Tesseract OCR Setup

For OCR capabilities (to handle scanned pages), you need to install Tesseract OCR:

- **Windows**: Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt install tesseract-ocr`

## Usage

1. Place the Kentucky Driver's Manual PDF (`Drivers-Manual-5-27-2021-Update.pdf`) in the project directory
2. Install the required dependencies:
   ```
   pip install -r requirements-dev.txt
   ```
3. Run the generator (creates `output/test_bank.json` plus coverage & stats):
   ```
   python simple_generator.py --pdf Drivers-Manual-5-27-2021-Update.pdf --output output --num_questions 400
   ```
4. (Optional) Run quality control and regenerate any problematic questions:
   ```
   python question_qc.py --input output/test_bank.json
   ```

## Quality Controls & Validity Assurance

The pipeline contains several automated safeguards that keep the questions educationally meaningful, exam-aligned, and diverse:

### During generation (`simple_generator.py`)
- Fixed difficulty distribution: 50 % easy, 35 % medium, 15 % hard. This matches the recommended study progression and ensures the user is challenged but not overwhelmed.
- Section coverage enforcement: every second-level heading of the manual is required to have ≥1 question; overall coverage is reported in `coverage_report.json`.
- Schema validation: each item is checked to have exactly four answer choices with one and only one marked correct, non-empty explanation, page reference, and tag list.
- Choice randomisation: answer order is shuffled per item to avoid positional bias.
- Tagging: every item is automatically categorised (e.g. `signs`, `speed`, `alcohol`) so later apps can create adaptive quizzes.

### Post-generation QC (`question_qc.py`)
- Banned-phrase filter: removes vague stems/choices such as "Follow Kentucky guidelines…" or "There are no specific rules…".
- Brevity limits: question stem ≤ 35 words; each choice ≤ 20 words.
- Explanation integrity: explanation must cite a page number from the manual.
- Correct-answer specificity: forbids generic or filler correct answers.
- Automatic regeneration: any item that fails a rule is rebuilt with concrete, manual-based facts.
- Distribution reconciliation: after fixes, the script verifies that difficulty ratios and section coverage still meet the original targets.

### Reporting
- `coverage_report.json` – per-section breakdown of items, difficulties, and % coverage.
- `stats.txt` – overall counts, average words per question, difficulty distribution, hardest section index.
- QC adds `qc_report.json` summarising how many items passed, were regenerated, and final distributions.

Together these controls create a balanced and authoritative test bank suitable for realistic Kentucky driver-licence exam preparation.