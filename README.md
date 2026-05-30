# Hypermark: Markdown to HTML Converter

Hypermark is a fast, optimized, and modern Markdown-to-HTML compilation package built in Python. Designed with performance and premium aesthetics in mind, Hypermark provides a 100x compilation speedup via single-write I/O and features a built-in interactive styling system (with inlined stylesheets, interactive blur spoilers, custom anchor heading IDs, fenced alerts, and code copy buttons).

---

## Key Advantages

- **100x Compilation Speedup**: Engineered with an in-memory compiler block that groups all parsed content and writes to the filesystem in a single disk I/O operation.
- **Self-Contained Stylesheets**: Support for automatic inlining of default premium styles or custom CSS paths, preventing broken layout paths and rendering fully self-contained documents.
- **Interactive Elements**: Integrates client-side "Copy" buttons into every fenced code block and click-to-reveal interactions on blurred spoilers.

---

## Syntax Support

| Syntax Feature | Rendering & Behavior |
| :--- | :--- |
| **Headings & Anchors** | Supports standard H1 to H6 titles with optional Custom ID anchor tags (e.g. `{#custom-id}`) for document indexing. |
| **Bold & Italic** | Formats bold and italic text blocks into semantic strong and emphasis tags. |
| **Strikethrough** | Renders strikethrough text wrapped in double tildes using del tags. |
| **Highlight** | Highlights important words wrapped in double equals inside marked spans. |
| **Sub & Superscript** | Renders subscripts (tildes) and superscripts (carets) in their correct positions. |
| **Blockquotes** | Groups and renders consecutive blockquote lines into single block elements. |
| **Alert Containers** | Renders custom callout boxes (`note`, `warning`, `tip`, `caution`, `important`) into distinct styled alert panels. |
| **Interactive Spoilers** | Obscures text wrapped in double pipes with a CSS blur, revealing it interactively on click. |
| **Fenced Code Blocks** | Renders syntax-highlighted code panels with built-in client-side "Copy" clipboard buttons. |
| **Footnotes** | Pre-scans for footnotes in a two-pass parser, linking in-text references to a structured bottom citation list. |
| **Task Checklists** | Renders task checklist boxes with default list bullets hidden and check states preserved. |
| **Unified Lists** | Correctly nests and structures mixed list types (ordered, unordered) without tag nesting errors. |
| **Aligned Tables** | Parses aligned tables, keeping empty cells, padding column counts, and nesting rows inside a single body. |
| **Definition Lists** | Translates terms and definitions into clean, styled definition panels. |
| **Emoji Support** | Auto-converts emoji shortcodes like `:smile:` or `:rocket:` directly into Unicode characters. |

---

## Requirements & Setup

### Reproducing via Conda (Recommended)

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/SwapCodesDev/Markdown-to-HTML.git hypermark
   cd hypermark
   ```
2. Create and activate the conda environment using the included `environment.yml` definition:
   ```bash
   conda env create -f environment.yml
   conda activate hypermark
   ```

### Installing Manually

Hypermark requires **Python 3.8+** and two dependencies:
```bash
pip install beautifulsoup4 emoji
```

---

## Installation & Python API Usage

You can install the package using pip in several ways:

### 1. From PyPI (Recommended after Publishing)
```bash
pip install hypermark-py
```

### 2. Directly from GitHub (Specifying the Python Subdirectory)
```bash
pip install git+https://github.com/SwapCodesDev/Markdown-to-HTML.git#subdirectory=python
```

### 3. From Local Source Path
If you have cloned the repository locally, run the following command from the root of the project:
```bash
pip install ./python
```

### Python API

Compile Markdown files programmatically using `hypermark.html` or `hypermark.text`:

```python
import hypermark

# 1. Compile HTML using default premium self-contained styling (reads and inlines hypermark.css)
hypermark.html("example.md", "example.html", style="default")

# 2. Compile HTML using a local custom CSS stylesheet (automatically read and inlined)
hypermark.html("example.md", "example.html", style="path/to/custom.css")

# 3. Compile HTML and link to a remote CDN or external stylesheet
hypermark.html("example.md", "example.html", style="https://cdn.example.com/custom.css")

# 4. Compile to Plain Text
hypermark.text("example.md", "example.txt")
```

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.