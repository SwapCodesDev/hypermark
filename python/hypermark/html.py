import re
import os
from typing import Optional, List, Dict, Tuple, Any
from bs4 import BeautifulSoup
import emoji
from .exceptions import ParserError, StyleSheetNotFoundError


class HTML:
    """Markdown to HTML Compiler with GFM alert boxes, spoilers, custom heading

    anchors, nested lists, and responsive table builders.
    """

    def __init__(self, path_md: str, path_html: str, style: str = "default", styles: Optional[str] = None) -> None:
        self.path_md: str = path_md
        self.path_html: str = path_html
        self.style: str = styles if styles is not None else style

        # State machine variables
        self.is_code_block: bool = False
        self.is_def_list: bool = False
        self.list_stack: List[Tuple[int, str]] = []
        self.paragraph_lines: List[str] = []
        self.blockquote_lines: List[str] = []
        self.table_lines: List[str] = []
        self.container_state: Dict[str, Any] = {
            'is_active': False,
            'type': 'note',
            'title': 'NOTE',
            'lines': []
        }

        self.html_content: List[str] = []
        self.code_block_stores: List[str] = []
        self.code_lines: List[str] = []
        self.footnotes: Dict[int, Tuple[str, str]] = {}

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
            with open(self.path_html, 'w', encoding="utf-8") as file:
                file.write(data)
            return True
        except PermissionError:
            raise PermissionError(f"Permission denied for writing to file: {self.path_html}")
        except Exception as e:
            raise ParserError(f"Unexpected error writing HTML output: {e}")

    def Handle_escaping_characters(self, line: str) -> str:
        line = re.sub(r'&', '&amp;', line)
        line = re.sub(r'<', '&lt;', line)
        line = re.sub(r'>', '&gt;', line)
        line = re.sub(r'"', '&quot;', line)
        line = re.sub(r"'", '&#39;', line)
        return line

    def convert_emoji(self, line: str) -> str:
        try:
            line = emoji.emojize(line)
        except ValueError:
            pass
        else:
            line = emoji.emojize(line, language="alias")
        return line

    def format_inline(self, text: str, footnotes: Optional[Dict[int, Tuple[str, str]]] = None) -> str:
        if not text:
            return ""

        placeholders: Dict[str, str] = {}
        p_counter = 0

        # 1. Protect & convert Inline Code
        def replace_code(match: re.Match[str]) -> str:
            nonlocal p_counter
            code_content = match.group(1)
            escaped_code = self.Handle_escaping_characters(code_content)
            html_val = f"<code>{escaped_code}</code>"
            placeholder = f"HYPERMARKPLACEHOLDERCODE{p_counter}"
            placeholders[placeholder] = html_val
            p_counter += 1
            return placeholder

        text = re.sub(r"`([^`]+)`", replace_code, text)

        # 2. Protect & convert Images (alt, url)
        def replace_image(match: re.Match[str]) -> str:
            nonlocal p_counter
            alt = match.group(1)
            url = match.group(2)
            alt = self.convert_emoji(alt)
            html_val = f'<img src="{url}" alt="{alt}">'
            placeholder = f"HYPERMARKPLACEHOLDERIMG{p_counter}"
            placeholders[placeholder] = html_val
            p_counter += 1
            return placeholder

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)

        # 3. Protect & convert Links (text, url)
        def replace_link(match: re.Match[str]) -> str:
            nonlocal p_counter
            link_text = match.group(1)
            url = match.group(2)
            formatted_link_text = self.format_inline(link_text, footnotes=None)
            html_val = f'<a href="{url}">{formatted_link_text}</a>'
            placeholder = f"HYPERMARKPLACEHOLDERLINK{p_counter}"
            placeholders[placeholder] = html_val
            p_counter += 1
            return placeholder

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)

        # 4. Handle Footnote References
        if footnotes is not None:
            def replace_footnote(match: re.Match[str]) -> str:
                nonlocal p_counter
                footnote_ref = match.group(1)
                matching_id = next((key for key, value in footnotes.items() if value[1] == footnote_ref), None)
                if matching_id is not None:
                    html_val = f'<sup><a href="#fn{footnote_ref}" id="{footnote_ref}">^{matching_id}</a></sup>'
                    placeholder = f"HYPERMARKPLACEHOLDERFN{p_counter}"
                    placeholders[placeholder] = html_val
                    p_counter += 1
                    return placeholder
                return match.group(0)

            text = re.sub(r"\[\^([^\]]+)\](?!:)", replace_footnote, text)

        # 5. Escape raw text
        text = self.Handle_escaping_characters(text)

        # 6. Emojis
        text = self.convert_emoji(text)

        # 7. Apply conversions: Bold, Italic, Strikethrough, Subscript, Superscript, Highlight, Spoiler
        text = re.sub(r"(\*\*|__)(.*?)\1", r"<strong>\2</strong>", text)
        text = re.sub(r"(\*|_)(.*?)\1", r"<em>\2</em>", text)
        text = re.sub(r"~~(.*?)~~", r"<del>\1</del>", text)
        text = re.sub(r"==(.*?)==", r"<mark>\1</mark>", text)
        text = re.sub(r"~(.*?)~", r"<sub>\1</sub>", text)
        text = re.sub(r"\^(.*?)\^", r"<sup>\1</sup>", text)
        text = re.sub(
            r"\|\|(.*?)\|\|",
            '<span class="spoiler" title="Click to reveal" onclick="this.classList.toggle(\'revealed\')">\\1</span>',
            text
        )

        # 8. Restore placeholders
        for placeholder, html_val in placeholders.items():
            text = text.replace(placeholder, html_val)

        return text

    def convert_heading(self, line: str) -> str:
        level_match = re.match(r"^#+", line)
        assert level_match is not None
        level = len(level_match.group())
        content = line[level:].strip()

        id_match = re.search(r"\{\#([a-zA-Z0-9_-]+)\}\s*$", content)
        heading_id = ""
        if id_match:
            heading_id = id_match.group(1)
            content = content[:id_match.start()].strip()

        formatted_content = self.format_inline(content, self.footnotes)
        if heading_id:
            return f'<h{level} id="{heading_id}">{formatted_content}</h{level}>'
        else:
            return f'<h{level}>{formatted_content}</h{level}>'

    def convert_blockquote(self, lines: List[str]) -> str:
        formatted_lines = [f"<p>{self.format_inline(line, self.footnotes)}</p>" for line in lines]
        return "<blockquote>\n" + "\n".join(formatted_lines) + "\n</blockquote>"

    def convert_container(self, container_type: str, container_title: str, lines: List[str]) -> str:
        html_val = f'<div class="custom-block {container_type}">\n'
        html_val += f'  <p class="custom-block-title">{container_title}</p>\n'

        current_p: List[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_p:
                    html_val += f'  <p>{self.format_inline(" ".join(current_p), self.footnotes)}</p>\n'
                    current_p = []
            else:
                current_p.append(stripped)
        if current_p:
            html_val += f'  <p>{self.format_inline(" ".join(current_p), self.footnotes)}</p>\n'

        html_val += '</div>'
        return html_val

    def convert_table(self, lines: List[str]) -> str:
        if len(lines) < 2:
            return "\n".join(lines)

        sep_line = lines[1].strip()
        cleaned_sep = sep_line.replace('|', '').replace(':', '').replace('-', '').strip()
        is_valid_sep = len(cleaned_sep) == 0 and '-' in sep_line

        if not is_valid_sep:
            return "\n".join([f"<p>{self.format_inline(line, self.footnotes)}</p>" for line in lines])

        table_html = '<table style="border: 1px solid black; border-collapse: collapse;">\n'

        header_line = lines[0].strip()
        if header_line.startswith('|'):
            header_line = header_line[1:]
        if header_line.endswith('|'):
            header_line = header_line[:-1]
        headers = [h.strip() for h in header_line.split('|')]

        table_html += "  <thead>\n    <tr>\n"
        for h in headers:
            formatted_h = self.format_inline(h, self.footnotes)
            table_html += f"      <th style='border: 1px solid black; padding: 5px;'>{formatted_h}</th>\n"
        table_html += "    </tr>\n  </thead>\n"

        if sep_line.startswith('|'):
            sep_line = sep_line[1:]
        if sep_line.endswith('|'):
            sep_line = sep_line[:-1]
        align_cols = [c.strip() for c in sep_line.split('|')]
        alignments: List[str] = []
        for c in align_cols:
            if c.startswith(':') and c.endswith(':'):
                alignments.append('center')
            elif c.endswith(':'):
                alignments.append('right')
            else:
                alignments.append('left')

        while len(alignments) < len(headers):
            alignments.append('left')

        table_html += "  <tbody>\n"
        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue
            if line.startswith('|'):
                line = line[1:]
            if line.endswith('|'):
                line = line[:-1]
            cols = [c.strip() for c in line.split('|')]

            while len(cols) < len(headers):
                cols.append('')

            table_html += "    <tr>\n"
            for col, alignment in zip(cols[:len(headers)], alignments):
                formatted_col = self.format_inline(col, self.footnotes)
                table_html += f"      <td style='border: 1px solid black; padding: 5px; text-align: {alignment};'>{formatted_col}</td>\n"
            table_html += "    </tr>\n"

        table_html += "  </tbody>\n"
        table_html += '</table>\n'
        return table_html

    def flush_blocks(self) -> None:
        if self.list_stack:
            while self.list_stack:
                _, ltype = self.list_stack.pop()
                self.html_content.append(f"</{ltype}>")

        if self.paragraph_lines:
            p_text = " ".join(self.paragraph_lines)
            self.html_content.append(f"<p>{self.format_inline(p_text, self.footnotes)}</p>")
            self.paragraph_lines.clear()

        if self.blockquote_lines:
            self.html_content.append(self.convert_blockquote(self.blockquote_lines))
            self.blockquote_lines.clear()

        if self.table_lines:
            self.html_content.append(self.convert_table(self.table_lines))
            self.table_lines.clear()

        if self.container_state['is_active']:
            self.html_content.append(self.convert_container(
                self.container_state['type'],
                self.container_state['title'],
                self.container_state['lines']
            ))
            self.container_state['is_active'] = False
            self.container_state['lines'] = []

        if self.is_def_list:
            self.html_content.append("</dl>")
            self.is_def_list = False

    def convert(self) -> None:
        lines = self.read()
        if lines is None:
            return

        # Setup CSS styling block
        css_content = ""
        css_link = ""

        style_normalized = self.style.lower().strip() if isinstance(self.style, str) else ""
        if style_normalized in ("default", "defualt"):
            # Try package-bundled stylesheet first
            package_css_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "hypermark.css")
            )
            # Try development repository root path as a secondary option
            repo_css_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "resources", "hypermark.css")
            )
            
            for path in (package_css_path, repo_css_path):
                if os.path.exists(path):
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            css_content = f.read()
                            break
                    except Exception:
                        pass
            
            if not css_content:
                css_link = "<link rel='stylesheet' href='https://cdn.jsdelivr.net/gh/SwapCodesDev/hypermark@master/resources/hypermark.css'>\n"
        elif self.style and os.path.exists(self.style):
            try:
                with open(self.style, "r", encoding="utf-8") as f:
                    css_content = f.read()
            except Exception as e:
                raise StyleSheetNotFoundError(f"Error loading custom stylesheet at {self.style}: {e}")
        elif self.style:
            css_link = f"<link rel='stylesheet' href='{self.style}'>\n"

        html_initial_body = (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\">\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "  <title>Markdown to HTML</title>\n"
            "  <!-- Highlight.js Styles -->\n"
            "  <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css\">\n"
        )

        if css_content:
            html_initial_body += f"  <style>\n{css_content}\n  </style>\n"
        elif css_link:
            html_initial_body += f"  {css_link}"

        html_initial_body += (
            "  <script src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js\"></script>\n"
            "  <script src=\"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/go.min.js\"></script>\n"
            "</head>\n"
            "<body>\n"
        )

        html_end_body = (
            "  <script>\n"
            "  hljs.highlightAll();\n"
            "  function copyCode(button) {\n"
            "    const container = button.closest('.code-block-container');\n"
            "    const code = container.querySelector('code');\n"
            "    navigator.clipboard.writeText(code.innerText).then(() => {\n"
            "      button.textContent = 'Copied!';\n"
            "      button.classList.add('copied');\n"
            "      setTimeout(() => {\n"
            "        button.textContent = 'Copy code';\n"
            "        button.classList.remove('copied');\n"
            "      }, 2000);\n"
            "    });\n"
            "  }\n"
            "  </script>\n"
            "</body>\n"
            "</html>"
        )

        # PASS 1: Footnote pre-scan
        for raw_line in lines:
            line = raw_line.replace('\r', '').replace('\n', '')
            fn_def_match = re.match(r"^\[\^([^\]]+)\]:\s*(.*)", line)
            if fn_def_match:
                fn_ref = fn_def_match.group(1)
                fn_content = fn_def_match.group(2).strip()
                fn_id = len(self.footnotes) + 1
                self.footnotes[fn_id] = (self.format_inline(fn_content, footnotes=None), fn_ref)

        # PASS 2: Main loop
        for idx, raw_line in enumerate(lines):
            line = raw_line.replace('\r', '').replace('\n', '')

            # Code Blocks
            if line.strip().startswith("```"):
                if not self.is_code_block:
                    self.flush_blocks()
                    lang = line.strip()[3:].strip()
                    lang_class = f' class="language-{lang}"' if lang else ''
                    lang_display = lang if lang else 'code'
                    self.is_code_block = True
                    self.code_lines = []
                else:
                    code_text = "\n".join(self.code_lines)
                    block_html = (
                        f'<div class="code-block-container">\n'
                        f'  <div class="code-block-header">\n'
                        f'    <span class="code-block-lang">{lang_display}</span>\n'
                        f'    <button class="copy-code-button" onclick="copyCode(this)">Copy code</button>\n'
                        f'  </div>\n'
                        f'  <pre><code{lang_class}>{code_text}</code></pre>\n'
                        f'</div>'
                    )
                    placeholder = f"HYPERMARKBLOCKCODEBLOCKPLACEHOLDER{len(self.code_block_stores)}"
                    self.code_block_stores.append(block_html)
                    self.html_content.append(placeholder)
                    self.is_code_block = False
                continue

            if self.is_code_block:
                self.code_lines.append(self.Handle_escaping_characters(line))
                continue

            # Fenced Containers
            if line.strip().startswith(":::"):
                if not self.container_state['is_active']:
                    self.flush_blocks()
                    parts = line.strip()[3:].strip().split(maxsplit=1)
                    c_type = parts[0] if parts else 'note'
                    c_title = parts[1] if len(parts) > 1 else c_type.upper()
                    self.container_state['is_active'] = True
                    self.container_state['type'] = c_type
                    self.container_state['title'] = c_title
                    self.container_state['lines'] = []
                else:
                    self.html_content.append(self.convert_container(
                        self.container_state['type'],
                        self.container_state['title'],
                        self.container_state['lines']
                    ))
                    self.container_state['is_active'] = False
                    self.container_state['lines'] = []
                continue

            if self.container_state['is_active']:
                self.container_state['lines'].append(line)
                continue

            # Footnote definitions
            if re.match(r"^\[\^([^\]]+)\]:\s*(.*)", line):
                self.flush_blocks()
                continue

            # Blank Lines
            if not line.strip():
                self.flush_blocks()
                self.html_content.append("")
                continue

            # Headings
            if line.startswith("#"):
                self.flush_blocks()
                self.html_content.append(self.convert_heading(line))
                continue

            # Horizontal Rule
            if line.strip() == "---":
                self.flush_blocks()
                self.html_content.append("<hr>")
                continue

            # Blockquote
            if line.startswith(">"):
                if not self.blockquote_lines:
                    self.flush_blocks()
                self.blockquote_lines.append(line[1:])
                continue

            # Tables
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

            # Lists
            list_match = re.match(r"^(\s*)(\d+\.\s+|[-\+\*]\s+)(.*)", line)
            if list_match:
                if not self.list_stack:
                    self.flush_blocks()

                indent = len(list_match.group(1))
                marker = list_match.group(2).strip()
                content = list_match.group(3).strip()
                list_type = "ol" if marker.endswith('.') else "ul"

                task_match = re.match(r"^\[([ xX])\]\s+(.*)", content)
                if task_match:
                    checked = task_match.group(1).lower() == 'x'
                    item_content = task_match.group(2).strip()
                    is_task = True
                else:
                    item_content = content
                    is_task = False

                while self.list_stack and indent < self.list_stack[-1][0]:
                    _, closed_type = self.list_stack.pop()
                    self.html_content.append(f"</{closed_type}>")

                if not self.list_stack or indent > self.list_stack[-1][0]:
                    self.list_stack.append((indent, list_type))
                    self.html_content.append(f"<{list_type}>")
                elif indent == self.list_stack[-1][0] and list_type != self.list_stack[-1][1]:
                    _, closed_type = self.list_stack.pop()
                    self.html_content.append(f"</{closed_type}>")
                    self.list_stack.append((indent, list_type))
                    self.html_content.append(f"<{list_type}>")

                formatted_content = self.format_inline(item_content, self.footnotes)
                if is_task:
                    chk = "checked" if checked else ""
                    self.html_content.append(
                        f'<li style="list-style-type: none;"><input type="checkbox" {chk} disabled> {formatted_content}</li>'
                    )
                else:
                    self.html_content.append(f'<li>{formatted_content}</li>')
                continue

            # Definition list
            if line.startswith(":"):
                if not self.is_def_list:
                    if self.list_stack or self.blockquote_lines or self.table_lines or self.container_state['is_active']:
                        self.flush_blocks()

                    term_text = " ".join(self.paragraph_lines)
                    self.paragraph_lines.clear()

                    self.html_content.append("<dl>")
                    self.html_content.append(f"<dt>{self.format_inline(term_text, self.footnotes)}</dt>")
                    self.is_def_list = True

                definition_text = line[1:].strip()
                self.html_content.append(f"<dd>{self.format_inline(definition_text, self.footnotes)}</dd>")
                continue

            # Fallback: Paragraph
            if self.list_stack or self.blockquote_lines or self.table_lines or self.container_state['is_active']:
                self.flush_blocks()

            self.paragraph_lines.append(line.strip())

        self.flush_blocks()

        if self.footnotes:
            self.html_content.append("<hr><h3>Footnotes</h3><ol>")
            for fn_id, content in self.footnotes.items():
                self.html_content.append(
                    f'<li id="fn{content[1]}">{content[0]} <a href="#{content[1]}">^{fn_id}</a></li>'
                )
            self.html_content.append("</ol>")

        full_html = html_initial_body + "\n".join(self.html_content) + "\n" + html_end_body

        try:
            soup = BeautifulSoup(full_html, "html.parser")
            final_html = soup.prettify()
        except Exception as e:
            # Fallback to full HTML if BS4 parsing fails
            final_html = full_html

        for idx, block_html in enumerate(self.code_block_stores):
            placeholder = f"HYPERMARKBLOCKCODEBLOCKPLACEHOLDER{idx}"
            final_html = re.sub(rf"\s*{placeholder}\s*", f"\n{block_html}\n", final_html)

        self.write(final_html)


def html(path_md: str, path_html: str, style: str = "default", styles: Optional[str] = None) -> None:
    """Convenience functional wrapper to parse Markdown into stylized HTML."""
    parser = HTML(path_md, path_html, style=style, styles=styles)
    parser.convert()
