import sys
import os
import tempfile
from bs4 import BeautifulSoup

# Ensure local hypermark is preferred in testing path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))

import hypermark  # type: ignore


def test_html_headings_and_anchors():
    """Verify H1-H6 parsing and Custom Heading Anchor IDs."""
    md_content = """# Title
## Section {#custom-sec-id}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        h1 = soup.find("h1")
        assert h1 is not None
        assert h1.text.strip() == "Title"

        h2 = soup.find("h2")
        assert h2 is not None
        assert h2.text.strip() == "Section"
        assert h2.get("id") == "custom-sec-id"


def test_html_inlines_and_spoilers():
    """Verify bold, italics, highlights, subscripts, superscripts, and blurred spoilers."""
    md_content = "This is **bold**, *italic*, ==highlight==, ~sub~, ^super^, and a ||secret spoiler||."
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        assert soup.find("strong").text.strip() == "bold"
        assert soup.find("em").text.strip() == "italic"
        assert soup.find("mark").text.strip() == "highlight"
        assert soup.find("sub").text.strip() == "sub"
        assert soup.find("sup").text.strip() == "super"

        spoiler = soup.find("span", class_="spoiler")
        assert spoiler is not None
        assert spoiler.text.strip() == "secret spoiler"
        assert "revealed" not in spoiler.get("class")


def test_html_alert_containers():
    """Verify fenced custom alert containers are rendered as custom blocks."""
    md_content = """::: warning Urgent Alert
This is a warning block!
:::
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        alert = soup.find("div", class_="custom-block warning")
        assert alert is not None
        assert alert.find("p", class_="custom-block-title").text.strip() == "Urgent Alert"
        assert "warning block" in alert.text


def test_html_blockquotes_merging():
    """Verify consecutive blockquotes lines are correctly merged."""
    md_content = """> Quote line one
> Quote line two
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        quote = soup.find("blockquote")
        assert quote is not None
        paragraphs = quote.find_all("p")
        assert len(paragraphs) == 2
        assert paragraphs[0].text.strip() == "Quote line one"
        assert paragraphs[1].text.strip() == "Quote line two"


def test_html_lists_and_tasks():
    """Verify nested list structures and task checklist conversion."""
    md_content = """- Item A
- Item B
  - [x] Done Task
  - [ ] Pending Task
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        list_items = soup.find_all("li")
        assert len(list_items) == 4
        
        # Check task list checkboxes
        checked_task = list_items[2].find("input", type="checkbox")
        assert checked_task is not None
        assert checked_task.has_attr("checked")
        assert checked_task.has_attr("disabled")

        unchecked_task = list_items[3].find("input", type="checkbox")
        assert unchecked_task is not None
        assert not unchecked_task.has_attr("checked")
        assert unchecked_task.has_attr("disabled")


def test_html_tables():
    """Verify columns and row alignments inside tables."""
    md_content = """| Header A | Header B |
| :--- | ---: |
| Left aligned | Right aligned |
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        hypermark.html(md_file, html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        table = soup.find("table")
        assert table is not None
        
        headers = table.find_all("th")
        assert len(headers) == 2
        
        cells = table.find("tbody").find_all("td")
        assert len(cells) == 2
        assert "text-align: left" in cells[0].get("style")
        assert "text-align: right" in cells[1].get("style")
