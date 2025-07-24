# PDF Parsers

Collection and evaluation of open source PDF parsers

## Evaluations

A number of pdf parsers are evaluated on a set of documents in the `docs/` folder.
The documents are in English and Swedish, and the purpose of this repository is first
and foremost to evaluate PDF parsers to find which one is best suited to be used for
a digital assistant for the the Swedish public sector.

Some of the documents have been selected specifically because the have proven tricky
to parse and others are selected to be representative of the type of documents that
would commonly be seen in real usage.

The parsers have been run on a laptop with a _13th Gen Intel(R) Core(TM) i9-13980HX_
CPU and an NVIDIA RTX 4080 GPU. All neural parsers have been run with cuda.

### Results

The resulting documents are saved in `out/<parser>/<document_name>` and in
`out/<parser>/parser_info.json` parsing times are stored per document and for each page
in the document.

The parsers that stand out the most are

- Llamaparse: Consistently good results. Handles tables and complex layouts rather well and convert to markdown, but only uses a single heading level. Unfortunately it is a paid product by Llama index. Use if you are OK with that. Can handle scanned documents
- Marker: Possibly the best fully open-source alternative, but can only be used for non-commersial projects. Can convert to markdown and handles complex layouts and probably has the most accurate heading levels and is quick to run. Can handle scanned documents
- Docling: Mostly high quality results and can convert to markdown, but only uses a single heading level. Sometimes be confused because it only considers a single page at once.
- Pdftext: Very fast and high quality parsing to plain text. Handles text order well and related text is clustered together. Sometimes creates new paragraphs in the middle of sentences
- PyMuPdf4LLM: PDF to markdown parser based on the GPL-licensed MuPDF. Has support for tables and headings, but the results are inconsistent. The best rule-based markdown parser for PDFs that I was able to identify.

## Installing and running evaluations

Install the dependencies: `uv sync`

Start the docker services: `docker compose up -d`

Run a test `uv run src/main.py <parser>` or all tests `./run_evals.sh`

## List of document parsers

| Name                                                                             | Source                                            | Target             | Thoughts                                                                                              | Type                                     | License               | Tested |
| -------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------------- | --------------------- | ------ |
| [docling](https://github.com/DS4SD/docling)                                      | pdf, docx, pptx, images, html                     | md, json           | Structured PDF understanding, including table structures. OCR support                                 | Python library / CLI                     | MIT                   | Yes    |
| [General OCR theory](https://huggingface.co/stepfun-ai/GOT-OCR2_0)               | Image                                             | text, tex          | End-to-end general OCR model                                                                          | Deep learning model                      | Apache                | Yes    |
| [Llamaparse](https://github.com/run-llama/llama_parse)                           | pdf, docx, pptx, xlsx, html                       | txt, md, json, xml | Structured PDF parser. Very high quality parsing                                                      | Hosted API service                       | Commercial            | Yes    |
| [LLMSherpa](https://github.com/nlmatics/llmsherpa)                               | PDF                                               | json, md           | Structured pdf parser. OK accuracy and speed. Uses hosted service                                     | Self-hosted API service                  | MIT                   | Yes    |
| [Marker](https://github.com/VikParuchuri/marker)                                 | pdf, docx                                         | txt                | Surya + rule-based with post processing                                                               | Python library / cli / hosted API        | GPL & cc-by-nc-sa-4.0 | Yes    |
| [markitdown](https://github.com/microsoft/markitdown)                            | PDF, images, pptx, docx, xlsx, audio, html, other | text               | Parsing of many different datatypes to text/markdown. Mostly glue code for other tools, e.g. pdfminer | Python library                           | MIT                   | Yes    |
| [Nougat](https://github.com/facebookresearch/nougat)                             | Image                                             | text               | OCR for pages from academic papers                                                                    | Python library                           | MIT                   | Yes    |
| [pdfminer.six](https://github.com/pdfminer/pdfminer.six)                         | PDF                                               | txt, html, xml     | Pretty good and fast. Extracted html is messy                                                         | python library                           | MIT                   | Yes    |
| [pdfplumber](https://github.com/jsvine/pdfplumber)                               | PDF                                               | txt                | Based on pdfminer.six. Can extract structured documents. Difficulty with multi-column text            | python library                           | MIT                   | Yes    |
| [pdftext](https://github.com/VikParuchuri/pdftext)                               | PDF                                               | text, json         | Structured pdf parser. Like PyMuPDF but permissive license. Based on pypdfium2                        | Python library / CLI                     | Apache                | Yes    |
| [MuPDF](https://mupdf.com/)                                                      | PDF                                               | txt, md, html      | High quality, extracts tables                                                                         | library                                  | AGPL                  | Yes    |
| [PyPDF](https://github.com/py-pdf/pypdf)                                         | PDF                                               | txt                | Slow and often splits words incorrectly                                                               | python library                           | permissive            | Yes    |
| [pypdfium](https://github.com/pypdfium2-team/pypdfium2/tree/stable)              | PDF                                               | text               | Low level PDF library using pdfium                                                                    | Python library                           | Apache                | Yes    |
| [Unstructured](https://github.com/Unstructured-IO/unstructured)                  | Many                                              | txt                | Extracts text from many sources. Rule-based and OCR. Not better than other solutions                  | Python library                           | Apache                | Yes    |
| [Gemini-2.0-Flash](https://deepmind.google/technologies/gemini/flash/)           | Image                                             | Any                | Cheap but powerful multimodal LLM with a free tier. Heard good things for OCR                         | LLM                                      | Commercial            | Yes    |
| [Parsr](https://github.com/axa-group/Parsr)                                      | Image, pdf, docx                                  | json, md, csv, txt | OCR + pdfminer with a lot of cleaning rules. Pretty slow but good                                     | Self-hosted API service                  | Apache                | No     |
| [Surya](https://github.com/VikParuchuri/surya)                                   | Image                                             | txt                | OCR 90+ languages, layout analysis, table recognition                                                 | Python library                           | GPL & cc-by-nc-sa-4.0 | No     |
| [tabled-pdf](https://github.com/VikParuchuri/tabled)                             | Image                                             | md, csv, html      | Extracts tables with OCR. Uses surya                                                                  |                                          | GPL & cc-by-nc-sa-4.0 | No     |
| [texify](https://github.com/VikParuchuri/texify)                                 | Image                                             | latex equations    | OCR for latex equations or equations with inline text                                                 | Python library                           | GPL & cc-by-nc-sa-4.0 | No     |
| [LaTeX-OCR](https://github.com/lukas-blecher/LaTeX-OCR)                          | Image                                             | latex equations    | OCR for latex equations. Hallucinates on text                                                         | Python library / GUI                     | MIT                   | No     |
| [Donut](https://github.com/clovaai/donut/)                                       | Image                                             | text               | Base model for OCR                                                                                    | Python library                           | MIT                   | No     |
| [mammoth](https://github.com/mwilliamson/mammoth.js)                             | docx                                              | html               | Converts docx files to html and maintains structure                                                   | JS/Python library / CLI                  | BSD-2                 | No     |
| [paper2html](https://github.com/ktaaaki/paper2html)                              | PDF                                               | html               | Extracts HTML from academic pdfs                                                                      | Python library / self-hosted API service | AGPL                  | No     |
| [LaTeXML](https://github.com/brucemiller/LaTeXML)                                | tex, latex                                        | xml, html          | Converts latex to html                                                                                | CLI                                      | Public domain         | No     |
| [pandoc](https://github.com/jgm/pandoc)                                          | many                                              | many               | Conversion between many types of documents but not pdfs                                               | CLI                                      | GPL-2                 | No     |
| [turndown](https://github.com/mixmark-io/turndown)                               | html                                              | md                 |                                                                                                       | JS library                               | MIT                   | No     |
| [html-to-markdown](https://github.com/JohannesKaufmann/html-to-markdown)         | html                                              | md                 | Converts HTML to markdown with cleanup to make it work with entire websites. Extensible               | Go library / CLI / hosted API            | MIT                   | No     |
| [tesseract](https://github.com/tesseract-ocr/tesseract)                          | Image                                             | text               | OCR engine                                                                                            | C/C++ API and CLI                        | Apache                | No     |
| [GROBID](https://github.com/kermitt2/grobid)                                     | PDF                                               | xml                | Structured pdf understanding with deep learning models (not OCR)                                      | Self hosted API service                  | Apache                | No     |
| [markdownify](https://github.com/matthewwithanm/python-markdownify)              | html                                              | md                 | Convert html to md                                                                                    | Python library                           | MIT                   | No     |
| [DeepDoc](https://github.com/infiniflow/ragflow/tree/main/deepdoc)               | PDF, images                                       | text               | Parsing of diverse documents to text with rule-based and OCR                                          | Python library                           | Apache                | No     |
| [markdownify](https://github.com/matthewwithanm/python-markdownify/tree/develop) | html                                              | md                 | Converts HTML to markdown with cleaning                                                               | Python library                           | MIT                   | No     |
