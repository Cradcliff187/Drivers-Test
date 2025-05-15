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
- Required Python packages (install via `pip install -r requirements.txt`):
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
   pip install -r requirements.txt
   ```
3. Run the generator:
   ```
   python generate_and_fix.py
   ```

### Command Line Options

- `--pdf PATH`: Path to the PDF file (default: "Drivers-Manual-5-27-2021-Update.pdf")
- `--output DIR`: Directory for output files (default: "output")
- `--num_questions N`: Number of questions to generate (default: 400)
- `--extract_images`: Extract images from the PDF for image-based questions

Example:
```
python run_generator.py --pdf Drivers-Manual-5-27-2021-Update.pdf --num_questions 500 --extract_images
```

## Enhanced Question Generator

This project includes an enhanced question generation and fixing pipeline:

```
python generate_and_fix.py
```

This command:
1. Generates raw questions using the simple generator
2. Applies an enhanced fixing algorithm to improve question quality
3. Runs quality control checks to ensure all questions meet standards

### Previewing Enhanced Questions

To preview the enhanced questions:

```
python preview_enhanced.py --compare
```

Options:
- `--input PATH`: Path to the question bank file (default: "output/enhanced_test_bank.json")
- `--compare`: Show side-by-side comparison with original questions
- `--num N`: Number of questions to preview (default: 5)
- `--filter TEXT`: Filter questions by section or content

## Output Files

The generator creates several output files in the specified output directory:

1. `test_bank.json`: The raw generated test bank before enhancements
2. `enhanced_test_bank.json`: The improved test bank after question fixing
3. `coverage_report.json`: Statistics on section coverage and question distribution
4. `qc_report.json`: Quality control report showing pass/fail metrics
5. `stats.txt`: Human-readable summary of the test bank generation

If image extraction is enabled, images will be saved to an `images` subdirectory.

## Test Bank JSON Format

Each question in the test bank follows this structure:

```json
{
  "questionID": "KDM-00001",
  "sectionID": "RulesOfTheRoad.RightOfWay",
  "difficulty": "easy",
  "questionText": "When two vehicles arrive at an intersection at the same time, which driver has the right-of-way?",
  "choices": [
    {"label": "A", "text": "The car on the left", "isCorrect": false},
    {"label": "B", "text": "The car on the right", "isCorrect": true},
    {"label": "C", "text": "The faster car", "isCorrect": false},
    {"label": "D", "text": "The heavier vehicle", "isCorrect": false}
  ],
  "explanation": "According to the Kentucky Driver's Manual on page 37, the driver on the right has the right-of-way when two vehicles arrive at an intersection at the same time.",
  "pageRef": 37,
  "tags": ["right-of-way", "intersections"],
  "requiresImage": false,
  "imagePrompt": null
}
```

## License

This project is intended for educational purposes only. The Kentucky State Driver's Manual is the property of the Commonwealth of Kentucky.

## Acknowledgments

- Kentucky Transportation Cabinet for providing the Driver's Manual
- This project uses open-source libraries for PDF processing, text extraction, and natural language processing 