import io
import re
import os
import fitz  # PyMuPDF
import numpy as np
from tqdm import tqdm
import warnings

# Try importing pytesseract, but don't fail if it's not available
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except (ImportError, Exception):
    warnings.warn("pytesseract or Tesseract OCR not available. OCR capabilities will be disabled.")
    TESSERACT_AVAILABLE = False

class KentuckyManualProcessor:
    """
    Specialized processor for the Kentucky Driver's Manual
    with enhanced text extraction, OCR capabilities, and TOC parsing
    """
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_count = len(self.doc)
        self.toc = []
        self.section_map = {}
        
    def extract_all_text(self):
        """Extract text from all pages with OCR fallback for poor quality pages"""
        pages_text = {}
        
        for page_num in tqdm(range(self.page_count), desc="Extracting text"):
            page = self.doc[page_num]
            text = page.get_text("text")
            
            # If text extraction yields too little text, try OCR if available
            if len(text.strip()) < 100 and TESSERACT_AVAILABLE:  # Arbitrary threshold
                try:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text_ocr = pytesseract.image_to_string(img)
                    if len(text_ocr.strip()) > len(text.strip()):
                        text = text_ocr
                except Exception as e:
                    print(f"OCR failed for page {page_num + 1}: {str(e)}")
            
            pages_text[page_num + 1] = text
            
        return pages_text
    
    def extract_table_of_contents(self):
        """Extract TOC from the document"""
        # First, try to get TOC from document metadata
        doc_toc = self.doc.get_toc()
        
        if doc_toc:
            # Convert to our format
            for item in doc_toc:
                level, title, page = item
                self.toc.append({
                    "level": level,
                    "title": title,
                    "page": page
                })
        else:
            # Try to find TOC pages and parse them
            toc_pages = self._find_toc_pages()
            if toc_pages:
                self._parse_toc_from_pages(toc_pages)
            else:
                # As a last resort, try to extract headings from the document
                self._extract_headings_as_toc()
        
        return self._structure_toc()
    
    def _find_toc_pages(self):
        """Find pages that are likely to contain the table of contents"""
        toc_pages = []
        
        # Look for pages with "Table of Contents", "Contents", etc.
        for page_num in range(min(10, self.page_count)):  # Check first 10 pages
            page = self.doc[page_num]
            text = page.get_text("text").lower()
            if "content" in text and "table" in text:
                toc_pages.append(page_num)
                # Also include the next page if TOC likely continues
                if page_num + 1 < self.page_count:
                    toc_pages.append(page_num + 1)
                    
        return toc_pages
    
    def _parse_toc_from_pages(self, page_nums):
        """Parse TOC from the identified TOC pages"""
        toc_text = ""
        for page_num in page_nums:
            page = self.doc[page_num]
            toc_text += page.get_text("text")
        
        # Use regex to find patterns like "Chapter Title..........23"
        matches = re.finditer(r'([^\n.]+)\.{2,}\s*(\d+)', toc_text)
        for match in matches:
            title = match.group(1).strip()
            page = int(match.group(2))
            
            # Determine level based on indentation or formatting
            level = 1
            if title.startswith('    '):
                level = 2
            elif title.startswith('        '):
                level = 3
                
            self.toc.append({
                "level": level,
                "title": title.lstrip(),
                "page": page
            })
    
    def _extract_headings_as_toc(self):
        """Fall back to extracting headings directly from the document"""
        for page_num in range(self.page_count):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Look for spans with larger font or bold formatting
                            font_size = span["size"]
                            font_flags = span["flags"]  # 16 often indicates bold
                            text = span["text"].strip()
                            
                            if font_size > 12 and len(text) < 100 and len(text) > 3:
                                # Likely a heading
                                level = 1 if font_size > 14 else 2
                                
                                self.toc.append({
                                    "level": level,
                                    "title": text,
                                    "page": page_num + 1
                                })
    
    def _structure_toc(self):
        """Convert flat TOC list into hierarchical structure with section IDs"""
        structured_sections = []
        section_id_counter = {"": 0}  # To generate sequential IDs within each level
        current_parents = [""] * 10  # To track parent at each level
        
        # First pass: create section objects with IDs
        for item in self.toc:
            level = item["level"]
            parent_id = current_parents[level - 1]
            
            # Generate ID based on parent and counter
            if parent_id not in section_id_counter:
                section_id_counter[parent_id] = 0
            section_id_counter[parent_id] += 1
            
            if parent_id:
                section_id = f"{parent_id}.{section_id_counter[parent_id]}"
            else:
                section_id = f"Section{section_id_counter[parent_id]}"
            
            # Clean title to create component of section ID
            clean_title = re.sub(r'[^a-zA-Z0-9]', '', item["title"])
            if clean_title:
                section_id = f"{section_id}.{clean_title}"
            
            # Store current ID as parent for next level
            current_parents[level] = section_id
            
            # Calculate end page (will be updated in second pass)
            end_page = self.page_count if item == self.toc[-1] else item["page"]
            
            section = {
                "id": section_id,
                "title": item["title"],
                "level": level,
                "pageRange": [item["page"], end_page],
                "parent": parent_id if parent_id else None,
                "children": []
            }
            
            structured_sections.append(section)
            
            # Update section map for quick lookup
            self.section_map[section_id] = section
        
        # Second pass: update end pages and add children to parents
        for i in range(len(structured_sections) - 1):
            this_section = structured_sections[i]
            next_section = structured_sections[i + 1]
            
            # Update end page to one before start of next section at same or higher level
            if next_section["level"] <= this_section["level"]:
                this_section["pageRange"][1] = next_section["pageRange"][0] - 1
            
            # Add as child to parent
            if this_section["parent"] and this_section["parent"] in self.section_map:
                parent = self.section_map[this_section["parent"]]
                parent["children"].append(this_section["id"])
        
        return structured_sections
    
    def extract_images(self, output_dir="extracted_images"):
        """Extract images from PDF for potential use in image-based questions"""
        os.makedirs(output_dir, exist_ok=True)
        image_paths = []
        
        try:
            for page_num in range(self.page_count):
                page = self.doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = self.doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Generate descriptive filename
                    filename = f"page{page_num+1}_img{img_index}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, "wb") as img_file:
                        img_file.write(image_bytes)
                        
                    image_paths.append({
                        "path": filepath,
                        "page": page_num + 1,
                        "index": img_index
                    })
        except Exception as e:
            print(f"Error extracting images: {str(e)}")
        
        return image_paths
    
    def chunk_text_by_sections(self, pages_text):
        """Split text into chunks based on section boundaries"""
        chunks = []
        chunk_id = 1
        
        # For each section, extract text from its page range
        for section_id, section in self.section_map.items():
            section_text = ""
            start_page = section["pageRange"][0]
            end_page = section["pageRange"][1]
            
            # Collect all text in this section's page range
            for page_num in range(start_page, min(end_page + 1, self.page_count + 1)):
                if page_num in pages_text:
                    section_text += pages_text[page_num]
            
            # Split into smaller chunks
            paragraphs = section_text.split("\n\n")
            current_chunk = ""
            
            for para in paragraphs:
                if para.strip():
                    if len(current_chunk) + len(para) < 1000:
                        if current_chunk:
                            current_chunk += "\n\n"
                        current_chunk += para
                    else:
                        # Save current chunk and start a new one
                        if current_chunk:
                            chunks.append({
                                "id": f"chunk-{chunk_id}",
                                "text": current_chunk,
                                "section": section_id,
                                "pageNum": start_page  # Approximation
                            })
                            chunk_id += 1
                        current_chunk = para
            
            # Don't forget the last chunk
            if current_chunk:
                chunks.append({
                    "id": f"chunk-{chunk_id}",
                    "text": current_chunk,
                    "section": section_id,
                    "pageNum": start_page  # Approximation
                })
                chunk_id += 1
        
        return chunks
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close() 