from enum import StrEnum, auto
from functools import cache
from pathlib import Path
import os
import json

import pypdf
from pydantic import BaseModel
from dotenv import load_dotenv
from tqdm import tqdm
import typer
from google import genai

from src.utils import write_to_file
from src.parsers.base import BasePdfParser
import ollama

load_dotenv()

REPO_ROOT = Path(__name__).parent.parent
DOC_DIR = REPO_ROOT / "docs"
OUT_DIR = REPO_ROOT / "results"

if not OUT_DIR.exists():
    OUT_DIR.mkdir()

# Initialize Gemini client for evaluation
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY is None:
    raise ValueError("GOOGLE_API_KEY is not set for evaluation")

genai_client = genai.Client()


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
    # OCR_MAC = auto()
    # OPENAI_VISION = auto()
    PDFMINER = auto()
    PDFPLUMBER = auto()
    PDFPLUMBER_LAYOUT = auto()
    PDFTEXT = auto()
    # PDFTEXT_JSON = auto()
    PYMUPDF4LLM = auto()
    PYMUPDF = auto()
    PYPDF = auto()
    PYPDFIUM2 = auto()
    QWEN_VISION = auto()
    RAPIDOCR = auto()
    UNSTRUCTURED_FAST = auto()
    UNSTRUCTURED_HIRES = auto()
    # GOT_OCR2_0 = auto()
    # GOT_OCR2_0_FORMAT = auto()
    GEMINI_2_0_FLASH = auto()


class EvaluationMetrics(BaseModel):
    formatting_score: float  # 0-10
    structure_preservation: float  # 0-10
    content_accuracy: float  # 0-10
    readability: float  # 0-10
    overall_score: float  # 0-10
    feedback: str


class EvaluatedFileInfo(BaseModel):
    name: str
    n_pages: int
    load_time: float
    load_time_per_page: float
    evaluation: EvaluationMetrics


class EvaluatedParserInfo(BaseModel):
    name: str
    files_loaded: list[EvaluatedFileInfo]
    avg_load_time_per_page: float | None = None
    avg_formatting_score: float | None = None
    avg_structure_preservation: float | None = None
    avg_content_accuracy: float | None = None
    avg_readability: float | None = None
    avg_overall_score: float | None = None


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
    #if parser == Parser.GOT_OCR2_0:
    #     from parsers.got_ocr import GotOcrPdfParser

    #     return GotOcrPdfParser(mode="ocr")
    # if parser == Parser.GOT_OCR2_0_FORMAT:
    #     from parsers.got_ocr import GotOcrPdfParser

    #     return GotOcrPdfParser(mode="format")

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
    # if parser == Parser.OCR_MAC:
    #     from src.parsers.ocr_mac import OcrMacPdfParser

    #     return OcrMacPdfParser()
    # if parser == Parser.OPENAI_VISION:
    #     from src.parsers.openai_vision import OpenAIVisionPdfParser

    #     return OpenAIVisionPdfParser()
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
    try:
        pdf_reader = pypdf.PdfReader(path)
        return len(pdf_reader.pages)
    except Exception as e:
        print(f"Error reading PDF {path.name}: {e}")
        raise


def run_parser(parser_: Parser, max_docs: int = None, doc_path: str = None) -> ParserInfo:
    """
    Run a parser on documents and return parser info with timing data.
    
    Args:
        parser_: The parser to run
        max_docs: Maximum number of documents to process
        doc_path: Specific document path to test. If provided, only this document will be processed.
    """
    parser = get_parser(parser_)
    
    print(f"Running parser: {parser.__class__.__name__}")
    
    parser_out_dir = OUT_DIR / parser_.value
    parser_out_dir.mkdir(exist_ok=True)
    parser_info = ParserInfo(name=parser_.value, files_loaded=[])
    
    # Get list of documents to process
    if doc_path:
        # Use specific document path
        doc_path_obj = Path(doc_path)
        if not doc_path_obj.exists():
            raise FileNotFoundError(f"Document not found: {doc_path}")
        doc_files = [doc_path_obj]
        print(f"Processing specific document: {doc_path}")
    else:
        # Use documents from DOC_DIR
        doc_files = list(DOC_DIR.glob("*.pdf"))
        if max_docs:
            doc_files = doc_files[:max_docs]
    
    for doc_path in tqdm(doc_files, desc=f"Processing documents with {parser_.value}"):
        try:
            # Check page count before processing
            try:
                n_pages = get_n_pages(doc_path)
                if n_pages > 25:
                    print(f"Skipping {doc_path.name} - too many pages ({n_pages} > 25)")
                    continue
            except Exception as page_error:
                print(f"Error getting page count for {doc_path.name}: {page_error}")
                continue
            
            # Parse the document
            try:
                parser.parse(doc_path, parser_out_dir)
            except Exception as parse_error:
                print(f"Error parsing {doc_path.name} with {parser_.value}: {parse_error}")
                continue
            
            # Create file info
            try:
                loaded_file_info = LoadedFileInfo(
                    name=doc_path.name,
                    n_pages=n_pages,
                    load_time=parser.runtime,
                    load_time_per_page=parser.runtime / n_pages,
                )
                parser_info.files_loaded.append(loaded_file_info)
            except Exception as info_error:
                print(f"Error creating file info for {doc_path.name}: {info_error}")
                continue
            
        except Exception as e:
            print(f"Unexpected error processing {doc_path.name} with {parser_.value}: {e}")
            continue
    
    # Calculate average load time per page
    if parser_info.files_loaded:
        parser_info.avg_load_time_per_page = sum(
            [file_info.load_time_per_page for file_info in parser_info.files_loaded]
        ) / len(parser_info.files_loaded)
    
    # Save parser info
    try:
        parser_info_path = OUT_DIR / f"{parser_.value}_parser_info.json"
        write_to_file(parser_info_path, parser_info.model_dump_json(indent=4))
    except Exception as e:
        print(f"Error saving parser info for {parser_.value}: {e}")
        # Continue without saving - don't fail the entire process
    
    return parser_info


def evaluate_parser(parser_: Parser, parser_info: ParserInfo) -> EvaluatedParserInfo:
    """
    Evaluate a parser's output quality using OpenAI as an LLM evaluator.
    """
    print(f"Evaluating parser quality: {parser_.value}")
    
    parser_out_dir = OUT_DIR / parser_.value
    evaluated_parser_info = EvaluatedParserInfo(name=parser_.value, files_loaded=[])
    
    # Get all .md output files from the parser
    output_files = list(parser_out_dir.glob("*.md"))
    
    if not output_files:
        print(f"No .md output files found in {parser_out_dir}")
        return evaluated_parser_info
    
    for output_file in tqdm(output_files, desc=f"Evaluating {parser_.value} outputs"):
        # Find corresponding original PDF
        original_pdf = DOC_DIR / output_file.with_suffix('.pdf').name
        if not original_pdf.exists():
            print(f"Original PDF not found for {output_file.name}")
            continue
        
        # Read the parser output
        if not output_file.exists():
            evaluation = EvaluationMetrics(
                formatting_score=0.0,
                structure_preservation=0.0,
                content_accuracy=0.0,
                readability=0.0,
                overall_score=0.0,
                feedback="Parser output file not found"
            )
        else:
            with open(output_file, 'r', encoding='utf-8') as f:
                parser_output = f.read()
            
            # Create evaluation prompt
            evaluation_prompt = f"""
            You are an expert evaluator of PDF parsing quality. Evaluate the following parser output based on these criteria:

            **Original PDF**: {original_pdf.name}
            **Parser Output**:
            ```
            {parser_output[:5000]}  # Limit to first 5000 chars to avoid token limits
            ```

            Please evaluate this parser output on a scale of 0-10 for each metric:

            1. **Formatting Score (0-10)**: How well does the output preserve the original formatting, including:
               - Text alignment and spacing
               - Headers, subheaders, and text hierarchy
               - Lists, tables, and special formatting (if a block of text does not make sense, it is likely the parser failed to format the information)
               - Font emphasis (bold, italic, etc.)

            2. **Structure Preservation (0-10)**: How well does the output maintain the document structure:
               - Logical flow and organization
               - Section divisions and headings
               - Page breaks and layout structure
               - Document outline and navigation

            3. **Content Accuracy (0-10)**: How accurately does the output capture the original content:
               - Text completeness and fidelity
               - No missing or corrupted text
               - Proper character encoding
               - Preservation of numbers, dates, and special characters

            4. **Readability (0-10)**: How readable and usable is the output:
               - Clear and coherent text flow
               - Proper sentence and paragraph breaks
               - Logical text ordering
               - Absence of garbled or nonsensical text

            5. **Overall Score (0-10)**: Overall quality assessment considering all factors above

            Respond with a JSON object in this exact format:
            {{
                "formatting_score": <float>,
                "structure_preservation": <float>,
                "content_accuracy": <float>,
                "readability": <float>,
                "overall_score": <float>,
                "feedback": "<detailed feedback explaining the scores>"
            }}
            """

            try:
                # response = genai_client.models.generate_content(
                #    model="gemini-1.5-flash",
                #    contents=evaluation_prompt
                # )
                response = ollama.chat(
                    model='llama3.1:8b',  # or your chosen model
                    messages=[{
                        'role': 'user',
                        'content': evaluation_prompt
                    }],
                    options={
                        'temperature': 0.1,  # Low temperature for consistent evaluation
                        'num_predict': 1000,  # Limit response length
                    }
                )

                # Parse the JSON response
                response_text = response.message.content.strip().replace("```json", "").replace("```", "")
                
                # Clean the JSON string to handle control characters
                import re
                # Remove or replace problematic control characters
                response_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_text)
                # Handle escaped quotes and newlines in the feedback field
                response_text = response_text.replace('\\n', ' ').replace('\\"', '"')
                
                try:
                    evaluation_data = json.loads(response_text)
                    
                    evaluation = EvaluationMetrics(
                        formatting_score=float(evaluation_data["formatting_score"]),
                        structure_preservation=float(evaluation_data["structure_preservation"]),
                        content_accuracy=float(evaluation_data["content_accuracy"]),
                        readability=float(evaluation_data["readability"]),
                        overall_score=float(evaluation_data["overall_score"]),
                        feedback=evaluation_data["feedback"]
                    )
                except (json.JSONDecodeError, KeyError, ValueError) as json_error:
                    print(f"JSON parsing error: {json_error}")
                    print(f"Response text: {response_text[:500]}...")
                    # Fallback: try to extract scores using regex
                    import re
                    scores = {}
                    for field in ["formatting_score", "structure_preservation", "content_accuracy", "readability", "overall_score"]:
                        match = re.search(f'"{field}":\\s*([0-9.]+)', response_text)
                        scores[field] = float(match.group(1)) if match else 0.0
                    
                    evaluation = EvaluationMetrics(
                        formatting_score=scores.get("formatting_score", 0.0),
                        structure_preservation=scores.get("structure_preservation", 0.0),
                        content_accuracy=scores.get("content_accuracy", 0.0),
                        readability=scores.get("readability", 0.0),
                        overall_score=scores.get("overall_score", 0.0),
                        feedback="JSON parsing failed, scores extracted using regex fallback"
                    )
            
            except Exception as e:
                evaluation = EvaluationMetrics(
                    formatting_score=0.0,
                    structure_preservation=0.0,
                    content_accuracy=0.0,
                    readability=0.0,
                    overall_score=0.0,
                    feedback=f"Evaluation failed: {str(e)}"
                )
        
        # Get page count and timing info from parser_info
        n_pages = get_n_pages(original_pdf)
        load_time = 0.0
        load_time_per_page = 0.0
        
        # Find matching file info from parser_info
        for file_info in parser_info.files_loaded:
            if file_info.name == original_pdf.name:
                load_time = file_info.load_time
                load_time_per_page = file_info.load_time_per_page
                break
        
        evaluated_file_info = EvaluatedFileInfo(
            name=output_file.name,
            n_pages=n_pages,
            load_time=load_time,
            load_time_per_page=load_time_per_page,
            evaluation=evaluation
        )
        evaluated_parser_info.files_loaded.append(evaluated_file_info)
    
    # Calculate averages
    if evaluated_parser_info.files_loaded:
        evaluations = [file.evaluation for file in evaluated_parser_info.files_loaded]
        evaluated_parser_info.avg_formatting_score = sum(e.formatting_score for e in evaluations) / len(evaluations)
        evaluated_parser_info.avg_structure_preservation = sum(e.structure_preservation for e in evaluations) / len(evaluations)
        evaluated_parser_info.avg_content_accuracy = sum(e.content_accuracy for e in evaluations) / len(evaluations)
        evaluated_parser_info.avg_readability = sum(e.readability for e in evaluations) / len(evaluations)
        evaluated_parser_info.avg_overall_score = sum(e.overall_score for e in evaluations) / len(evaluations)
        
        # Calculate average load time per page
        load_times = [file.load_time_per_page for file in evaluated_parser_info.files_loaded if file.load_time_per_page > 0]
        if load_times:
            evaluated_parser_info.avg_load_time_per_page = sum(load_times) / len(load_times)
    
    # Save evaluation results
    try:
        write_to_file(
            OUT_DIR / f"{parser_.value}_evaluation_results.json", 
            evaluated_parser_info.model_dump_json(indent=4)
        )
    except Exception as e:
        print(f"Error saving evaluation results for {parser_.value}: {e}")
        # Continue without saving - don't fail the entire process
    
    # Print summary
    print(f"\nEvaluation Summary for {parser_.value}:")
    print(f"Files evaluated: {len(evaluated_parser_info.files_loaded)}")
    if evaluated_parser_info.avg_overall_score is not None:
        print(f"Average Overall Score: {evaluated_parser_info.avg_overall_score:.2f}/10")
        print(f"Average Formatting Score: {evaluated_parser_info.avg_formatting_score:.2f}/10")
        print(f"Average Structure Preservation: {evaluated_parser_info.avg_structure_preservation:.2f}/10")
        print(f"Average Content Accuracy: {evaluated_parser_info.avg_content_accuracy:.2f}/10")
        print(f"Average Readability: {evaluated_parser_info.avg_readability:.2f}/10")
        if evaluated_parser_info.avg_load_time_per_page:
            print(f"Average Load Time per Page: {evaluated_parser_info.avg_load_time_per_page:.3f}s")
    
    return evaluated_parser_info


def main(
    parsers: list[Parser] = None,
    max_docs: int = 20,
    skip_evaluation: bool = False,
    skip_parsing: bool = False,
    doc_path: str = None,
    skip_existing: bool = False
):
    """
    Run all parsers and evaluate their output.
    
    Args:
        parsers: List of parsers to run. If None, runs all parsers.
        max_docs: Maximum number of documents to process per parser.
        skip_evaluation: Skip the evaluation step.
        skip_parsing: Skip the parsing step (useful for re-evaluating existing outputs).
        doc_path: Specific document path to test. If provided, only this document will be processed.
        skip_existing: Skip parsers that already have output files in the results directory.
    """
    if parsers is None:
        parsers = list(Parser)
    
    # Track parsers that already have outputs if skip_existing is True
    skipped_parsers = []
    if skip_existing:
        original_count = len(parsers)
        
        for parser in parsers:
            parser_out_dir = OUT_DIR / parser.value
            if parser_out_dir.exists() and any(parser_out_dir.glob("*.md")):
                skipped_parsers.append(parser)
                print(f"Skipping {parser.value} - already has output files")
        
        parsers = [p for p in parsers if p not in skipped_parsers]
        skipped_count = original_count - len(parsers)
        if skipped_count > 0:
            print(f"Skipped {skipped_count} parsers with existing outputs")
    
    print(f"Processing {len(parsers)} parsers")
    if max_docs:
        print(f"Maximum documents per parser: {max_docs}")
    if doc_path:
        print(f"Testing with specific document: {doc_path}")
    if skip_existing:
        print(f"Skip existing outputs: {skip_existing}")
    
    all_results = {}
    
    # Load existing results for skipped parsers
    if skip_existing and skipped_parsers:
        print(f"\nLoading existing results for {len(skipped_parsers)} skipped parsers...")
        for parser in skipped_parsers:
            try:
                # Load parser info
                parser_info = None
                parser_info_path = OUT_DIR / f"{parser.value}_parser_info.json"
                if parser_info_path.exists():
                    with open(parser_info_path, 'r') as f:
                        data = json.load(f)
                    parser_info = ParserInfo(**data)
                
                # Load evaluation info
                evaluated_info = None
                eval_info_path = OUT_DIR / f"{parser.value}_evaluation_results.json"
                if eval_info_path.exists():
                    with open(eval_info_path, 'r') as f:
                        data = json.load(f)
                    evaluated_info = EvaluatedParserInfo(**data)
                
                all_results[parser.value] = {
                    'parser_info': parser_info,
                    'evaluated_info': evaluated_info
                }
                print(f"Loaded existing results for {parser.value}")
                
            except Exception as e:
                print(f"Error loading existing results for {parser.value}: {e}")
                continue
    
    for parser in parsers:
        print(f"\n{'='*60}")
        print(f"Processing parser: {parser.value}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Run the parser
            if not skip_parsing:
                parser_info = run_parser(parser, max_docs, doc_path)
            else:
                # Load existing parser info if skipping parsing
                parser_info_path = OUT_DIR / f"{parser.value}_parser_info.json"
                if parser_info_path.exists():
                    with open(parser_info_path, 'r') as f:
                        data = json.load(f)
                    parser_info = ParserInfo(**data)
                else:
                    print(f"No existing parser info found for {parser.value}")
                    continue
            
            # Step 2: Evaluate the parser output
            if not skip_evaluation:
                evaluated_info = evaluate_parser(parser, parser_info)
                all_results[parser.value] = {
                    'parser_info': parser_info,
                    'evaluated_info': evaluated_info
                }
            else:
                all_results[parser.value] = {
                    'parser_info': parser_info,
                    'evaluated_info': None
                }
                
        except Exception as e:
            print(f"Error processing parser {parser.value}: {e}")
            continue
    
    # Save comprehensive results
    if all_results:
        results_summary = {
            'summary': {
                'total_parsers': len(all_results),
                'parsers_processed': list(all_results.keys())
            },
            'results': {}
        }
        
        for parser_name, result in all_results.items():
            results_summary['results'][parser_name] = {
                'parser_info': result['parser_info'].model_dump() if result['parser_info'] else None,
                'evaluated_info': result['evaluated_info'].model_dump() if result['evaluated_info'] else None
            }
        
        write_to_file(
            OUT_DIR / "all_parsers_results.json",
            json.dumps(results_summary, indent=4)
        )
        
        print(f"\n{'='*60}")
        print("COMPREHENSIVE RESULTS SUMMARY")
        print(f"{'='*60}")
        
        # Print summary table
        print(f"{'Parser':<20} {'Files':<6} {'Avg Score':<10} {'Avg Time/Page':<15}")
        print("-" * 60)
        
        for parser_name, result in all_results.items():
            files_count = len(result['parser_info'].files_loaded) if result['parser_info'] else 0
            avg_score = result['evaluated_info'].avg_overall_score if result['evaluated_info'] else None
            avg_time = result['evaluated_info'].avg_load_time_per_page if result['evaluated_info'] else None
            
            score_str = f"{avg_score:.2f}" if avg_score is not None else "N/A"
            time_str = f"{avg_time:.3f}s" if avg_time is not None else "N/A"
            
            print(f"{parser_name:<20} {files_count:<6} {score_str:<10} {time_str:<15}")


if __name__ == "__main__":
    typer.run(main) 