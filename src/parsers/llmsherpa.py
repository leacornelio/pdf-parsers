from pathlib import Path

from llmsherpa.readers import LayoutPDFReader

from src.parsers.base import BasePdfParser


class LlmsherpaPdfParser(BasePdfParser):
    def __init__(self) -> None:
        super().__init__()
        self.reader = LayoutPDFReader(
            "http://localhost:5010/api/parseDocument?renderFormat=all"
        )

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        doc = self.reader.read_pdf(str(in_path))
        txt = doc.to_text()
        html = doc.to_html()
        return [(".txt", txt), (".html", html)]
