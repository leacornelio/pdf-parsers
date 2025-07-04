import os
from pathlib import Path
from pdf2image import convert_from_path
import easyocr
import numpy as np
from tqdm import tqdm

from src.parsers.base import BasePdfParser


class EasyOcrPdfParser(BasePdfParser):
    def __init__(self, languages: list = None) -> None:
        super().__init__()
        # Default to English if no languages specified
        self.languages = languages or ['en']
        self.reader = easyocr.Reader(self.languages)

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        # Convert PDF to images
        images = convert_from_path(in_path)
        
        all_text = []
        for i, image in enumerate(tqdm(images, desc="Processing pages", leave=False)):
            # Convert PIL Image to numpy array for EasyOCR
            image_array = np.array(image)
            
            # Perform OCR on each page
            results = self.reader.readtext(image_array)
            
            # Extract text from results
            page_text = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Filter by confidence threshold
                    page_text.append(text)
            
            # Join text with newlines
            page_content = '\n'.join(page_text)
            all_text.append(f"--- Page {i+1} ---\n{page_content}")
        
        return [(".txt", "\n\n".join(all_text))] 