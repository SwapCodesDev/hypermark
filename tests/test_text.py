import sys
import os
import tempfile

# Ensure local hypermark is preferred in testing path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))

import hypermark  # type: ignore


def test_text_link_and_image_stripping():
    """Verify raw URLs are completely stripped from links and images are formatted nicely for TTS."""
    md_content = "Please read [The Markdown Guide](https://www.markdownguide.org) and see ![Alt Description](img.png)."
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.text(md_file, txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            txt_output = f.read().strip()

        # Omit URL, keep alt tag for images
        assert "https://www.markdownguide.org" not in txt_output
        assert "Please read The Markdown Guide" in txt_output
        assert "Image: Alt Description" in txt_output


def test_text_spoilers_and_footnotes():
    """Verify spoiler tags become vocal and footnote reference indicators are hidden from paragraphs."""
    md_content = """This is a secret spoiler: ||hypermark is fast||.
This sentence references a footnote[^fnref].

[^fnref]: The footnote contents.
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.text(md_file, txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            txt_output = f.read().strip()

        # Spoiler label, superscript index omitted from main sentence, footnote spoken definition
        assert "Spoiler: hypermark is fast" in txt_output
        assert "[^fnref]" not in txt_output
        assert "This sentence references a footnote." in txt_output
        assert "Footnote fnref: The footnote contents." in txt_output


def test_text_table_vocalizer():
    """Verify columns and row alignments inside tables are formatted as conversational sentences."""
    md_content = """| Product | Price | Qty |
| :--- | :---: | ---: |
| Apple | $1.20 | 5 |
| Orange | $0.80 | 10 |
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.text(md_file, txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            txt_output = f.read().strip()

        # Check conversation formats
        assert "Table data:" in txt_output
        assert "Row: Product: Apple; Price: $1.20; Qty: 5." in txt_output
        assert "Row: Product: Orange; Price: $0.80; Qty: 10." in txt_output
        assert "|" not in txt_output


def test_text_code_block_boundaries():
    """Verify code blocks have vocal boundaries."""
    md_content = """Here is code:
```python
def foo():
    pass
```
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.text(md_file, txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            txt_output = f.read().strip()

        assert "Code block starts:" in txt_output
        assert "def foo():" in txt_output
        assert "Code block ends." in txt_output


def test_text_checklists():
    """Verify checkboxes are translated to spoken wording."""
    md_content = """- [x] Finished Task
- [ ] Upcoming Task
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.text(md_file, txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            txt_output = f.read().strip()

        assert "Completed: Finished Task" in txt_output
        assert "Todo: Upcoming Task" in txt_output
        assert "[ ]" not in txt_output
        assert "[x]" not in txt_output
