import re
import emoji
from typing import Match


def strip_inline_formatting(text: str) -> str:
    """Strips all inline Markdown syntax, formatting labels, and symbols to make the

    text completely clean and optimized for Text-to-Speech (TTS) engines.
    """
    if not text:
        return ""

    # Strip image: ![alt](url) -> Image: alt (if alt exists), else empty
    def replace_image(match: Match[str]) -> str:
        alt = match.group(1).strip()
        return f"Image: {alt}" if alt else ""

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)

    # Strip link: [text](url) -> text (completely omitting URL to keep TTS clean)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

    # Strip footnote references completely from inline text (e.g. [^1] -> "")
    text = re.sub(r"\[\^([^\]]+)\](?!:)", "", text)

    # Strip bold/italic/strikethrough/highlight/sub/super
    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    text = re.sub(r"==(.*?)==", r"\1", text)
    text = re.sub(r"~(.*?)~", r"\1", text)
    text = re.sub(r"\^(.*?)\^", r"\1", text)

    # Clean spoilers: ||spoiler|| -> Spoiler: spoiler
    text = re.sub(r"\|\|(.*?)\|\|", r"Spoiler: \1", text)

    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Emojis shortcodes
    try:
        text = emoji.emojize(text)
    except Exception:
        pass
    return text
