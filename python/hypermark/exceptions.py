class HypermarkError(Exception):
    """Base exception for all Hypermark-related errors."""
    pass


class ParserError(HypermarkError):
    """Raised when Markdown compilation or parsing fails."""
    pass


class StyleSheetNotFoundError(HypermarkError):
    """Raised when a referenced local CSS file cannot be located on disk."""
    pass
