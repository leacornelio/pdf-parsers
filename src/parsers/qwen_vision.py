import os
import time
import math
from pathlib import Path
from pdf2image import convert_from_path
from tqdm import tqdm
import ollama

from src.parsers.base import BasePdfParser


def with_retry(wait_time, retries):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    t = max(wait_time ** math.sqrt(i + 1), 60)
                    print(f"Function failed. Retrying in {t:.2f} seconds. Error: {exc}")
                    time.sleep(t)
        return wrapper
    return decorator


class QwenVisionPdfParser(BasePdfParser):
    def __init__(self, model: str = "qwen2.5vl:7b", max_tokens: int = 4096) -> None:
        super().__init__()
        self.model = model
        self.max_tokens = max_tokens

    @with_retry(wait_time=10, retries=3)
    def generate(self, image_path: str) -> str:
        """Generate text from image using Ollama with Qwen Vision model"""
        # Read image file
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Extract all text from this document image. Preserve the formatting and structure as much as possible. Return only the extracted text without any additional commentary.",
                    "images": [image_data]
                }
            ],
            options={
                "num_predict": self.max_tokens,
                "temperature": 0.1,
            }
        )
        
        return response.message.content

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        # Convert PDF to images
        images = convert_from_path(in_path)
        
        all_text = []
        for i, image in enumerate(tqdm(images, desc="Processing pages", leave=False)):
            # Save image to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                image.save(tmp_file.name, "PNG")
                tmp_path = tmp_file.name
            
            try:
                # Generate text from image
                page_text = self.generate(tmp_path)
                all_text.append(f"--- Page {i+1} ---\n{page_text}")
            finally:
                # Clean up temporary file
                os.unlink(tmp_path)
        
        return [(".txt", "\n\n".join(all_text))] 