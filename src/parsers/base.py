from abc import ABC, abstractmethod
from pathlib import Path
from time import time

from src.utils import write_to_file


class BasePdfParser(ABC):
    def __init__(self) -> None:
        self._runtime: float | None = None

    @property
    def runtime(self) -> float:
        if self._runtime is not None:
            return self._runtime
        raise AttributeError("parse not run")

    @abstractmethod
    def _parse(self, in_path: Path) -> list[tuple[str, str]]: ...

    def parse(self, in_path: Path, out_dir: Path) -> None:
        t0 = time()
        result = self._parse(in_path)
        self._runtime = time() - t0
        
        # Find markdown content if available, otherwise convert text to markdown
        md_content = None
        txt_content = None
        json_content = None
        html_content = None
        
        for suffix, content in result:
            if suffix == ".md":
                md_content = content
            elif suffix == ".txt":
                txt_content = content
            elif suffix == ".json":
                json_content = content
            elif suffix == ".html":
                html_content = content
        
        # Use markdown content if available, otherwise convert text to markdown
        if md_content is not None:
            final_content = md_content
        elif txt_content is not None:
            # Convert plain text to markdown format
            final_content = self._text_to_markdown(txt_content)
        elif json_content is not None:
            # Convert JSON to markdown format
            final_content = self._json_to_markdown(json_content)
        elif html_content is not None:
            # Convert HTML to markdown format
            final_content = self._html_to_markdown(html_content)
        else:
            # If no text content found, use the first available content
            if result:
                _, content = result[0]
                final_content = self._text_to_markdown(content)
            else:
                final_content = ""
        
        # Always write as .md file
        write_to_file(out_dir / in_path.with_suffix(".md").name, final_content)
    
    def _text_to_markdown(self, text: str) -> str:
        """Convert plain text to markdown format"""
        if not text:
            return ""
        
        # Split into lines and process
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append("")
                continue
            
            # Try to detect headers (lines that are all caps or have specific patterns)
            if line.isupper() and len(line) > 3 and len(line) < 100:
                # Likely a header
                markdown_lines.append(f"## {line}")
            elif line.endswith(':') and len(line) < 50:
                # Likely a section header
                markdown_lines.append(f"### {line}")
            else:
                # Regular text
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def _json_to_markdown(self, json_content: str) -> str:
        """Convert JSON content to markdown format"""
        try:
            import json
            data = json.loads(json_content)
            
            # Convert JSON to a readable markdown format
            markdown_lines = []
            
            def process_dict(d, level=0):
                indent = "  " * level
                for key, value in d.items():
                    if isinstance(value, dict):
                        markdown_lines.append(f"{indent}- **{key}**:")
                        process_dict(value, level + 1)
                    elif isinstance(value, list):
                        markdown_lines.append(f"{indent}- **{key}**:")
                        for item in value:
                            if isinstance(item, dict):
                                process_dict(item, level + 1)
                            else:
                                markdown_lines.append(f"{indent}  - {item}")
                    else:
                        markdown_lines.append(f"{indent}- **{key}**: {value}")
            
            process_dict(data)
            return '\n'.join(markdown_lines)
            
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, treat as plain text
            return self._text_to_markdown(json_content)
    
    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to markdown format"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Convert to markdown
            return self._text_to_markdown(text)
            
        except ImportError:
            # If BeautifulSoup is not available, use simple text extraction
            import re
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', html_content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return self._text_to_markdown(text)
