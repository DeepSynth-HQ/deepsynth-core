import re


def format_telegram_markdown(text):
    """
    Format the text to be compatible with Telegram's Markdown
    Args:
        text: The text to format
    Returns:
        The formatted text
    """
    # Remove any existing line breaks at the start/end
    text = text.strip()

    # Replace **text** with *text* for bold
    # Telegram uses single asterisks for bold
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)

    # Handle numbered lists
    # Replace patterns like "1. " with "1) "
    text = re.sub(r"(\d+)\.\s", r"\1) ", text)

    # Handle bullet points
    # Replace "* " with "• "
    text = re.sub(r"^\*\s", "• ", text, flags=re.MULTILINE)

    # Handle nested bullet points
    # Replace "  * " with "  • "
    text = re.sub(r"^(\s+)\*\s", r"\1• ", text, flags=re.MULTILINE)

    # Add extra newline before headers
    text = re.sub(r"(?<!^)(?<![\n])(#+ )", r"\n\1", text)

    # Add extra newline after headers
    text = re.sub(r"(#+ .*?)(?!\n\n)(\n|$)", r"\1\n\n", text)

    # Ensure proper spacing after bullet points and numbered lists
    text = re.sub(r"(^[•\d)\s]+.*?)(?!\n\n)(\n|$)", r"\1\n\n", text, flags=re.MULTILINE)

    # Remove multiple consecutive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text
