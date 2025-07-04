import os
import time
import math
import base64
from pathlib import Path
from pdf2image import convert_from_path
from tqdm import tqdm
import requests

from src.parsers.base import BasePdfParser

API_KEY = os.getenv("QWEN_API_KEY")
API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/api/v1")
if API_KEY is None:
    raise ValueError("QWEN_API_KEY is not set")


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
    def __init__(self, model: str = "qwen-vl-plus", max_tokens: int = 4096) -> None:
        super().__init__()
        self.api_key = API_KEY
        self.api_base = API_BASE
        self.model = model
        self.max_tokens = max_tokens

    @with_retry(wait_time=10, retries=3)
    def generate(self, image_path: str) -> str:
        """Generate text from image using Qwen Vision API"""
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": "Extract all text from this document image. Preserve the formatting and structure as much as possible. Return only the extracted text without any additional commentary."
                            },
                            {
                                "image": image_data
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "max_tokens": self.max_tokens,
                "temperature": 0.1
            }
        }
        
        response = requests.post(
            f"{self.api_base}/services/aigc/text-generation/generation",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["output"]["choices"][0]["message"]["content"]

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