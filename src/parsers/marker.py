from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from src.parsers.base import BasePdfParser


class MarkerPdfParser(BasePdfParser):
    def __init__(self) -> None:
        super().__init__()
        print("Initializing Marker PDF parser")
        try:
            self.converter = PdfConverter(artifact_dict=create_model_dict())
            print("Marker PDF parser initialized")
        except Exception as e:
            print(f"Error initializing Marker PDF parser: {e}")
            print("This might be due to a compatibility issue with texify and transformers.")
            print("Consider updating or downgrading transformers to resolve this issue.")
            raise

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        rendered = self.converter(str(in_path))
        text, _, _ = text_from_rendered(rendered)
        
        return [(".md", text)]
