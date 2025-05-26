import re


def camelcase(text: str) -> str:
    """Convert strings into camel case.

    Args:
        string: String to convert.

    Returns:
        string: Camel case string.

    """
    if not text:
        return text
    return text[0].lower() + re.sub(
        r"[\-_\.\s]([a-z0-9])", lambda matched: matched.group(1).upper(), text[1:]
    )
