import os
from pathlib import Path
from pdf2image import convert_from_path
from rapidocr_onnxruntime import RapidOCR
from tqdm import tqdm

from src.parsers.base import BasePdfParser


class RapidOcrPdfParser(BasePdfParser):
    def __init__(self, use_gpu: bool = False) -> None:
        super().__init__()
        self.ocr = RapidOCR(use_gpu=use_gpu)

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        # Convert PDF to images
        images = convert_from_path(in_path)
        
        all_text = []
        for i, image in enumerate(tqdm(images, desc="Processing pages", leave=False)):
            try:
                # Perform OCR on each page
                results, _ = self.ocr(image)
                
                # Check if results is None or empty
                if results is None:
                    print(f"Warning: No OCR results for page {i+1} in {in_path.name}")
                    all_text.append(f"--- Page {i+1} ---\n[No text detected]")
                    continue
                
                # Extract text from results
                page_text = []
                for box, text, confidence in results:
                    if confidence > 0.5:  # Filter by confidence threshold
                        page_text.append(text)
                
                # Join text with newlines
                page_content = '\n'.join(page_text) if page_text else "[No text detected]"
                all_text.append(f"--- Page {i+1} ---\n{page_content}")
                
            except Exception as e:
                print(f"Error processing page {i+1} in {in_path.name}: {e}")
                all_text.append(f"--- Page {i+1} ---\n[Error processing page: {str(e)}]")
                continue
        
        return [(".txt", "\n\n".join(all_text))] 