from enum import StrEnum, auto
from functools import cache
from pathlib import Path

import pypdf
from pydantic import BaseModel
from tqdm import tqdm
import typer

from src.utils import write_to_file
from src.parsers.base import BasePdfParser

REPO_ROOT = Path(__name__).parent.parent
DOC_DIR = REPO_ROOT / "docs"
OUT_DIR = REPO_ROOT / "out"

if not OUT_DIR.exists():
    OUT_DIR.mkdir()


class LoadedFileInfo(BaseModel):
    name: str
    n_pages: int
    load_time: float
    load_time_per_page: float


class ParserInfo(BaseModel):
    name: str
    files_loaded: list[LoadedFileInfo]
    avg_load_time_per_page: float | None = None


class Parser(StrEnum):
    DOCLING = auto()
    EASYOCR = auto()
    LLAMA_PARSE_FAST = auto()
    LLAMA_PARSE = auto()
    LLMSHERPA = auto()
    MARKER = auto()
    MARKITDOWN = auto()
    NOUGAT = auto()
    OCR_MAC = auto()
    OPENAI_VISION = auto()
    PDFMINER = auto()
    PDFPLUMBER = auto()
    PDFPLUMBER_LAYOUT = auto()
    PDFTEXT = auto()
    PDFTEXT_JSON = auto()
    PYMUPDF4LLM = auto()
    PYMUPDF = auto()
    PYPDF = auto()
    PYPDFIUM2 = auto()
    QWEN_VISION = auto()
    RAPIDOCR = auto()
    UNSTRUCTURED_FAST = auto()
    UNSTRUCTURED_HIRES = auto()
    GOT_OCR2_0 = auto()
    GOT_OCR2_0_FORMAT = auto()
    GEMINI_2_0_FLASH = auto()


def main(parser_: Parser):
    parser = get_parser(parser_)

    print(f"Evaluating parser: {parser.__class__.__name__}")

    parser_out_dir = OUT_DIR / parser_.value
    parser_out_dir.mkdir(exist_ok=True)
    parser_info = ParserInfo(name=parser_.value, files_loaded=[])

    for doc_path in (
        pbar := tqdm(list(DOC_DIR.iterdir()), desc="Processing documents")
    ):
        pbar.set_postfix_str(doc_path.name)
        parser.parse(doc_path, parser_out_dir)

        n_pages = get_n_pages(doc_path)
        loaded_file_info = LoadedFileInfo(
            name=doc_path.name,
            n_pages=n_pages,
            load_time=parser.runtime,
            load_time_per_page=parser.runtime / n_pages,
        )
        parser_info.files_loaded.append(loaded_file_info)

    parser_info.avg_load_time_per_page = sum(
        [file_info.load_time_per_page for file_info in parser_info.files_loaded]
    ) / len(parser_info.files_loaded)

    write_to_file(
        parser_out_dir / "parser_info.json", parser_info.model_dump_json(indent=4)
    )


def get_parser(parser: Parser) -> BasePdfParser:
    """Import at runtime to speed up initialization"""
    if parser == Parser.DOCLING:
        from src.parsers.docling import DoclingPdfParser

        return DoclingPdfParser()
    if parser == Parser.EASYOCR:
        from src.parsers.easyocr_parser import EasyOcrPdfParser

        return EasyOcrPdfParser()
    if parser == Parser.GEMINI_2_0_FLASH:
        from parsers.gemini_2_0_flash import Gemini2FlashParser

        return Gemini2FlashParser()
    if parser == Parser.GOT_OCR2_0:
        from parsers.got_ocr import GotOcrPdfParser

        return GotOcrPdfParser(mode="ocr")
    if parser == Parser.GOT_OCR2_0_FORMAT:
        from parsers.got_ocr import GotOcrPdfParser

        return GotOcrPdfParser(mode="format")

    if parser == Parser.LLAMA_PARSE:
        from src.parsers.llamaparse import LlamaParsePdfParser

        return LlamaParsePdfParser(fast=False)
    if parser == Parser.LLAMA_PARSE_FAST:
        from src.parsers.llamaparse import LlamaParsePdfParser

        return LlamaParsePdfParser(fast=True)
    if parser == Parser.LLMSHERPA:
        from src.parsers.llmsherpa import LlmsherpaPdfParser

        return LlmsherpaPdfParser()
    if parser == Parser.MARKER:
        from src.parsers.marker import MarkerPdfParser

        return MarkerPdfParser()
    if parser == Parser.MARKITDOWN:
        from parsers.markitdown import MarkitdownPdfParser

        return MarkitdownPdfParser()
    if parser == Parser.NOUGAT:
        from src.parsers.nougat import NougatPdfParser

        return NougatPdfParser()
    if parser == Parser.OCR_MAC:
        from src.parsers.ocr_mac import OcrMacPdfParser

        return OcrMacPdfParser()
    if parser == Parser.OPENAI_VISION:
        from src.parsers.openai_vision import OpenAIVisionPdfParser

        return OpenAIVisionPdfParser()
    if parser == Parser.PDFMINER:
        from src.parsers.pdfminer import PdfMinerPdfParser

        return PdfMinerPdfParser()
    if parser == Parser.PDFPLUMBER:
        from src.parsers.pdfplumber import PdfPlumberPdfParser

        return PdfPlumberPdfParser()
    if parser == Parser.PDFPLUMBER_LAYOUT:
        from src.parsers.pdfplumber import PdfPlumberPdfParser

        return PdfPlumberPdfParser(layout=True)
    if parser == Parser.PDFTEXT:
        from src.parsers.pdftext import PdftextPdfParser

        return PdftextPdfParser(output="txt")
    if parser == Parser.PDFTEXT_JSON:
        from src.parsers.pdftext import PdftextPdfParser

        return PdftextPdfParser(output="json")
    if parser == Parser.PYMUPDF:
        from src.parsers.pymypdf import PyMuPdfPdfParser

        return PyMuPdfPdfParser()
    if parser == Parser.PYMUPDF4LLM:
        from src.parsers.pymupdf4llm import PyMuPdf4llmPdfParser

        return PyMuPdf4llmPdfParser()
    if parser == Parser.PYPDF:
        from src.parsers.pypdf import PyPDFParser

        return PyPDFParser()
    if parser == Parser.PYPDFIUM2:
        from parsers.pypdfium2 import Pypdfium2PdfParser

        return Pypdfium2PdfParser()
    if parser == Parser.QWEN_VISION:
        from src.parsers.qwen_vision import QwenVisionPdfParser

        return QwenVisionPdfParser()
    if parser == Parser.RAPIDOCR:
        from src.parsers.rapidocr import RapidOcrPdfParser

        return RapidOcrPdfParser()
    if parser == Parser.UNSTRUCTURED_FAST:
        from parsers.unstructured import UnstructuredPdfParser

        return UnstructuredPdfParser(strategy="fast")
    if parser == Parser.UNSTRUCTURED_HIRES:
        from parsers.unstructured import UnstructuredPdfParser

        return UnstructuredPdfParser(strategy="hi_res")

    raise NotImplementedError(f"Parser not implemented: {parser}")


@cache
def get_n_pages(path: Path) -> int:
    pdf_reader = pypdf.PdfReader(path)
    return len(pdf_reader.pages)


if __name__ == "__main__":
    typer.run(main)
