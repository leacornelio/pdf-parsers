# PDF Parser Evaluation Framework

An evaluation framework for comparing the performance and quality of various PDF parsing libraries and tools. This tool benchmarks multiple PDF parsers across different metrics including parsing speed, content accuracy, formatting preservation, and readability.

## Overview

This framework evaluates **21 different PDF parsers** using both performance metrics (parsing time) and quality metrics (evaluated by LLM). It's designed to help you choose the best PDF parser for your specific use case by providing objective comparisons across multiple dimensions.

## Supported Parsers

The framework currently supports the following PDF parsers:

### Traditional Text Extraction
- **PyPDF** - Pure Python PDF library
- **PyMuPDF** - Python bindings for MuPDF
- **PyMuPDF4LLM** - LLM-optimized version of PyMuPDF
- **PDFMiner** - Pure Python PDF parser with layout analysis
- **PDFPlumber** - Advanced PDF text extraction with layout preservation
- **PDFPlumber Layout** - PDFPlumber with enhanced layout detection
- **PDFText** - Simple text extraction utility
- **Pypdfium2** - Python bindings for PDFium

### OCR-Based Parsers
- **EasyOCR** - Deep learning-based OCR
- **RapidOCR** - Fast OCR solution
- **Nougat** - Academic paper OCR model

### LLM-Based Parsers
- **Docling** - IBM's document understanding framework
- **LlamaParse** - LlamaIndex's parsing service (fast & standard modes)
- **Marker** - Vision-based document parser
- **Unstructured** - Document preprocessing (fast & hi-res modes)
- **LLMSherpa** - Layout-aware parser for LLMs
- **MarkItDown** - Microsoft's document conversion tool

### Vision Model Parsers
- **Gemini 2.0 Flash** - Google's multimodal AI
- **Qwen Vision** - Alibaba's vision-language model

## Features

- **Performance Benchmarking**: Measure parsing time per page across different document types
- **LLM-based Quality Assessment**: Use AI to evaluate output quality based on formatting, structure preservation, content accuracy, and readabilic
- **Flexible Testing**: Test specific documents or run comprehensive benchmarks
- **Comprehensive Reporting**: Generate detailed reports with scores and insights
- **Skip Existing Results**: Resume evaluations without re-processing completed parsers

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd pdf-parser-evaluation
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```
GOOGLE_API_KEY=your_gemini_api_key  # For evaluation (if using Gemini)
LLAMA_CLOUD_API_KEY=your_llamaparse_key  # For LlamaParse
```

4. **Install Ollama** (for local LLM evaluation):
```bash
# Install Ollama and pull the evaluation model
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
```

## Project Structure

```
pdf-parser-evaluation/
├── src/
│   ├── parsers/          # Individual parser implementations
│   │   ├── base.py       # Base parser interface
│   │   ├── docling.py    # Docling parser
│   │   ├── pypdf.py      # PyPDF parser
│   │   └── ...           # Other parser implementations
│   └── utils.py          # Utility functions
├── docs/                 # PDF documents for testing
├── results/              # Parser outputs and evaluation results
├── main.py              # Main evaluation script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Usage

### Basic Usage

Run all parsers on up to 20 documents:
```bash
python main.py
```

### Advanced Options

**Test specific parsers**:
```bash
python main.py --parsers PYPDF DOCLING MARKER
```

**Test with a specific document**:
```bash
python main.py --doc-path /path/to/your/document.pdf
```

**Limit number of documents per parser**:
```bash
python main.py --max-docs 5
```

**Skip evaluation (parsing only)**:
```bash
python main.py --skip-evaluation
```

**Skip parsing (evaluation only)**:
```bash
python main.py --skip-parsing
```

**Skip parsers with existing results**:
```bash
python main.py --skip-existing
```

### Command Line Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `--parsers` | List | Specific parsers to run | All parsers |
| `--max-docs` | Int | Maximum documents per parser | 20 |
| `--skip-evaluation` | Bool | Skip quality evaluation | False |
| `--skip-parsing` | Bool | Skip parsing step | False |
| `--doc-path` | String | Test specific document | None |
| `--skip-existing` | Bool | Skip parsers with existing outputs | False |

## Evaluation Metrics

The framework evaluates each parser across five key dimensions:

### 1. Formatting Score (0-10)
- Text alignment and spacing preservation
- Headers, subheaders, and text hierarchy
- Lists, tables, and special formatting
- Font emphasis (bold, italic, etc.)

### 2. Structure Preservation (0-10)
- Logical flow and organization
- Section divisions and headings
- Page breaks and layout structure
- Document outline and navigation

### 3. Content Accuracy (0-10)
- Text completeness and fidelity
- No missing or corrupted text
- Proper character encoding
- Preservation of numbers, dates, and special characters

### 4. Readability (0-10)
- Clear and coherent text flow
- Proper sentence and paragraph breaks
- Logical text ordering
- Absence of garbled or nonsensical text

### 5. Overall Score (0-10)
- Comprehensive quality assessment
- Weighted combination of all factors above

## Output Files

The framework generates several output files:

### Parser Results
- `{parser_name}/` - Directory containing parsed markdown files
- `{parser_name}_parser_info.json` - Performance metrics and timing data
- `{parser_name}_evaluation_results.json` - Quality scores and detailed feedback

### Summary Reports
- `all_parsers_results.json` - Comprehensive results for all parsers
- Console output with summary table showing key metrics

## Adding New Parsers

To add a new parser:

1. **Create parser implementation**:
```python
# src/parsers/your_parser.py
from src.parsers.base import BasePdfParser

class YourPdfParser(BasePdfParser):
    def parse(self, pdf_path: Path, output_dir: Path) -> str:
        # Implement your parsing logic
        pass
```

2. **Add to parser enum**:
```python
# main.py
class Parser(StrEnum):
    # ... existing parsers
    YOUR_PARSER = auto()
```

3. **Add to parser factory**:
```python
# main.py - get_parser function
if parser == Parser.YOUR_PARSER:
    from src.parsers.your_parser import YourPdfParser
    return YourPdfParser()
```