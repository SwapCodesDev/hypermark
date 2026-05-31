import sys
import os
import tempfile
import subprocess

# Ensure local hypermark is preferred in testing path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))


def test_cli_html_compilation():
    """Verify standard HTML compilation via the command line interface."""
    md_content = "# Hello World"
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        html_file = os.path.join(tmpdir, "test.html")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Run CLI module command
        cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
        env = os.environ.copy()
        env["PYTHONPATH"] = cli_path + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, "-m", "hypermark.cli", md_file, html_file],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Successfully compiled Markdown to HTML" in result.stdout
        assert os.path.exists(html_file)

        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "<h1>" in content
        assert "Hello World" in content


def test_cli_text_compilation():
    """Verify standard plain text compilation via the command line interface using -t / --text."""
    md_content = "Here is a [Link](https://google.com) to search."
    with tempfile.TemporaryDirectory() as tmpdir:
        md_file = os.path.join(tmpdir, "test.md")
        txt_file = os.path.join(tmpdir, "test.txt")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Run CLI module command
        cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
        env = os.environ.copy()
        env["PYTHONPATH"] = cli_path + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, "-m", "hypermark.cli", md_file, txt_file, "-t"],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Successfully compiled Markdown to Plain Text" in result.stdout
        assert os.path.exists(txt_file)

        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        assert "https://google.com" not in content
        assert "Here is a Link to search." in content


def test_cli_file_not_found():
    """Verify the CLI correctly returns exit code 2 when the input file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        non_existent_file = os.path.join(tmpdir, "ghost.md")
        output_file = os.path.join(tmpdir, "ghost.html")

        cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python"))
        env = os.environ.copy()
        env["PYTHONPATH"] = cli_path + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, "-m", "hypermark.cli", non_existent_file, output_file],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 2
        assert "File Error" in result.stderr
