import argparse
import sys
from .html import html
from .text import text
from .exceptions import HypermarkError


def main() -> None:
    """Main CLI entry point for compiling Markdown files via terminal commands."""
    parser = argparse.ArgumentParser(
        description="Hypermark - Fast and Modular Markdown to HTML/TTS-Text Compiler."
    )
    parser.add_argument("input", help="Path to the input Markdown (.md) file.")
    parser.add_argument("output", help="Path to the output compiled file.")
    parser.add_argument(
        "--style", "-s",
        default="default",
        help="Stylesheet for HTML compilation (either 'default' or path to custom CSS). Default is 'default'."
    )
    parser.add_argument(
        "--text", "-t",
        action="store_true",
        help="Compile directly to plain text optimized for TTS engines instead of HTML."
    )

    args = parser.parse_args()

    try:
        if args.text:
            text(args.input, args.output)
            print(f"Successfully compiled Markdown to Plain Text at: {args.output}")
        else:
            html(args.input, args.output, args.style)
            print(f"Successfully compiled Markdown to HTML at: {args.output}")
    except FileNotFoundError as e:
        print(f"File Error: {e}", file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f"Permission Error: {e}", file=sys.stderr)
        sys.exit(3)
    except HypermarkError as e:
        print(f"Compiler Error: {e}", file=sys.stderr)
        sys.exit(4)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(5)


if __name__ == "__main__":
    main()
