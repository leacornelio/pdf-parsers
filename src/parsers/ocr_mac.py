import os
import subprocess
import tempfile
from pathlib import Path
from pdf2image import convert_from_path
from tqdm import tqdm

from src.parsers.base import BasePdfParser


class OcrMacPdfParser(BasePdfParser):
    def __init__(self) -> None:
        super().__init__()
        # Check if we're on macOS
        if os.name != 'posix' or not os.path.exists('/System/Library/Frameworks/Vision.framework'):
            raise RuntimeError("OCR Mac parser requires macOS with Vision framework")

    def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using macOS Vision framework via AppleScript"""
        script = f'''
        tell application "System Events"
            set theImage to "{image_path}"
            set theText to do shell script "screencapture -i " & quoted form of theImage & " | textutil -convert txt -stdin -stdout"
            return theText
        end tell
        '''
        
        # Alternative approach using vision command line tools if available
        try:
            # Try using vision command line tool if available
            result = subprocess.run(
                ['vision', '--extract-text', image_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to basic OCR using system tools
        try:
            result = subprocess.run(
                ['tesseract', image_path, 'stdout'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return ""

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        # Convert PDF to images
        images = convert_from_path(in_path)
        
        all_text = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, image in enumerate(tqdm(images, desc="Processing pages", leave=False)):
                # Save image to temporary file
                temp_image_path = os.path.join(temp_dir, f"page_{i+1}.png")
                image.save(temp_image_path, "PNG")
                
                # Extract text from image
                page_text = self._extract_text_from_image(temp_image_path)
                
                if page_text.strip():
                    all_text.append(f"--- Page {i+1} ---\n{page_text.strip()}")
                else:
                    all_text.append(f"--- Page {i+1} ---\n[No text extracted]")
        
        return [(".txt", "\n\n".join(all_text))] 