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
3. Run the generator:
   ```