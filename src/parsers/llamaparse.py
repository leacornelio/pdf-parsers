import os
from pathlib import Path

from llama_parse import LlamaParse, ResultType

from src.parsers.base import BasePdfParser
from dotenv import load_dotenv

load_dotenv()


class LlamaParsePdfParser(BasePdfParser):
    def __init__(self, fast: bool = False) -> None:
        super().__init__()
        result_type = ResultType.TXT if fast else ResultType.MD
        self.parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY", ""),
            result_type=result_type,
            fast_mode=fast,
        )
        self.suffix = {ResultType.MD: ".md", ResultType.TXT: ".txt"}[result_type]

    def _parse(self, in_path: Path) -> list[tuple[str, str]]:
        documents = self.parser.load_data(str(in_path))
        if not documents:
            raise RuntimeError(f"Error parsing {in_path}")
        content = "\n\n".join(doc.text for doc in documents)
        return [(self.suffix, content)]
