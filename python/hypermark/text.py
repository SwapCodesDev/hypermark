import re
from typing import List
from .utils import strip_inline_formatting
from .exceptions import ParserError


class Text:
    """Markdown to TTS-Optimized Plain-Text Compiler. Removes all brackets,

    hyphens, asterisks, URLs, and footnote indices to make text readable by voice engines.
    """

    def __init__(self, path_md: str, path_text: str) -> None:
        self.path_md: str = path_md
        self.path_text: str = path_text
        self.text_content: List[str] = []

        # State machine variables
        self.is_code_block: bool = False
        self.paragraph_lines: List[str] = []
        self.blockquote_lines: List[str] = []
        self.table_lines: List[str] = []

    def read(self) -> List[str]:
        try:
            with open(self.path_md, 'r', encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Markdown file not found at: {self.path_md}")
        except PermissionError:
            raise PermissionError(f"Permission denied for file: {self.path_md}")
        except Exception as e:
            raise ParserError(f"Unexpected error reading markdown: {e}")

    def write(self, data: str) -> bool:
        try:
            with open(self.path_text, 'w', encoding="utf-8") as file:
                file.write(data)
            return True
        except PermissionError:
            raise PermissionError(f"Permission denied for writing to file: {self.path_text}")
        except Exception as e:
            raise ParserError(f"Unexpected error writing plain text: {e}")

    def flush_table(self, table_lines: List[str]) -> str:
        if not table_lines:
            return ""

        if len(table_lines) < 2:
            return "\n".join([strip_inline_formatting(line) for line in table_lines])

        sep_line = table_lines[1].strip()
        cleaned_sep = sep_line.replace('|', '').replace(':', '').replace('-', '').strip()
        is_valid_sep = len(cleaned_sep) == 0 and '-' in sep_line

        if not is_valid_sep:
            return "\n".join([strip_inline_formatting(line) for line in table_lines])

        formatted_rows: List[str] = []
        header_line = table_lines[0].strip()
        if header_line.startswith('|'):
            header_line = header_line[1:]
        if header_line.endswith('|'):
            header_line = header_line[:-1]
        headers = [strip_inline_formatting(h.strip()) for h in header_line.split('|')]

        for line in table_lines[2:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]
            cols = [strip_inline_formatting(c.strip()) for c in line.split('|')]

            row_parts: List[str] = []
            for idx, col in enumerate(cols):
                header = headers[idx] if idx < len(headers) else f"Column {idx + 1}"
                if header and col:
                    row_parts.append(f"{header}: {col}")
                elif col:
                    row_parts.append(col)
            if row_parts:
                formatted_rows.append("Row: " + "; ".join(row_parts) + ".")

        if formatted_rows:
            return "Table data:\n" + "\n".join(formatted_rows)
        return ""

    def flush_blocks(self) -> None:
        if self.paragraph_lines:
            p_text = " ".join(self.paragraph_lines)
            self.text_content.append(strip_inline_formatting(p_text))
            self.paragraph_lines.clear()

        if self.blockquote_lines:
            for line in self.blockquote_lines:
                self.text_content.append(f"  {strip_inline_formatting(line)}")
            self.blockquote_lines.clear()

        if self.table_lines:
            self.text_content.append(self.flush_table(self.table_lines))
            self.table_lines.clear()

    def convert(self) -> None:
        lines = self.read()
        if lines is None:
            return

        for idx, raw_line in enumerate(lines):
            line = raw_line.replace('\r', '').replace('\n', '')

            # Code Blocks
            if line.strip().startswith("```"):
                if not self.is_code_block:
                    self.flush_blocks()
                    self.is_code_block = True
                    self.text_content.append("\nCode block starts:\n")
                else:
                    self.is_code_block = False
                    self.text_content.append("\nCode block ends.\n")
                continue

            if self.is_code_block:
                self.text_content.append(line)
                continue

            # Blank Lines
            if not line.strip():
                self.flush_blocks()
                self.text_content.append("")
                continue

            # Horizontal Rule
            if line.strip() == "---":
                self.flush_blocks()
                self.text_content.append("")
                continue

            # Fenced Containers (Alert Boxes)
            if line.strip().startswith(":::"):
                self.flush_blocks()
                parts = line.strip()[3:].strip().split(maxsplit=1)
                if parts:
                    c_type = parts[0]
                    c_title = parts[1] if len(parts) > 1 else c_type.upper()
                    self.text_content.append(f"\n{c_title}:\n")
                continue

            # Heading
            if line.startswith("#"):
                self.flush_blocks()
                level_match = re.match(r"^#+", line)
                assert level_match is not None
                level = len(level_match.group())
                content = line[level:].strip()
                content = re.sub(r"\{\#([a-zA-Z0-9_-]+)\}\s*$", "", content).strip()
                stripped_content = strip_inline_formatting(content)
                self.text_content.append(f"\n{stripped_content}\n")
                continue

            # Blockquote
            if line.startswith(">"):
                if not self.blockquote_lines:
                    self.flush_blocks()
                self.blockquote_lines.append(line[1:])
                continue

            # Table
            if "|" in line:
                if self.table_lines:
                    self.table_lines.append(line)
                    continue
                else:
                    has_separator = False
                    if idx + 1 < len(lines):
                        next_line = lines[idx + 1].replace('\r', '').replace('\n', '').strip()
                        cleaned_sep = next_line.replace('|', '').replace(':', '').replace('-', '').strip()
                        has_separator = len(cleaned_sep) == 0 and '-' in next_line

                    if has_separator:
                        self.flush_blocks()
                        self.table_lines.append(line)
                        continue

            # Definition List
            if line.startswith(":"):
                if self.blockquote_lines or self.table_lines:
                    self.flush_blocks()

                term_text = " ".join(self.paragraph_lines)
                self.paragraph_lines.clear()

                if term_text:
                    self.text_content.append(strip_inline_formatting(term_text))

                content = line[1:].strip()
                self.text_content.append(f"    {strip_inline_formatting(content)}")
                continue

            # List Item
            list_match = re.match(r"^(\s*)(\d+\.\s+|[-\+\*]\s+)(.*)", line)
            if list_match:
                self.flush_blocks()
                indent = list_match.group(1)
                marker = list_match.group(2).strip()
                content = list_match.group(3).strip()

                # Check for task checkbox
                task_match = re.match(r"^\[([ xX])\]\s+(.*)", content)
                if task_match:
                    checked = task_match.group(1).lower() == 'x'
                    item_content = task_match.group(2).strip()
                    status = "Completed: " if checked else "Todo: "
                    stripped_content = status + strip_inline_formatting(item_content)
                else:
                    stripped_content = strip_inline_formatting(content)

                if marker.endswith('.'):
                    self.text_content.append(f"{indent}{marker} {stripped_content}")
                else:
                    self.text_content.append(f"{indent}{stripped_content}")
                continue

            # Footnote definitions
            fn_def_match = re.match(r"^\[\^([^\]]+)\]:\s*(.*)", line)
            if fn_def_match:
                self.flush_blocks()
                fn_ref = fn_def_match.group(1)
                fn_content = fn_def_match.group(2).strip()
                self.text_content.append(f"Footnote {fn_ref}: {strip_inline_formatting(fn_content)}")
                continue

            # Fallback: Paragraph
            if self.blockquote_lines or self.table_lines:
                self.flush_blocks()
            self.paragraph_lines.append(line.strip())

        self.flush_blocks()

        final_text = "\n".join(self.text_content)
        self.write(final_text)


def text(path_md: str, path_text: str) -> None:
    """Convenience functional wrapper to parse Markdown into TTS-optimized text."""
    parser = Text(path_md, path_text)
    parser.convert()
