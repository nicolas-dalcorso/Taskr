"""Defines several functions for wrapping, modifying and formatting text.
"""

import re
import textwrap
from typing import List, Tuple

def wrap_text(text: str, width: int) -> List[str]:
    """Wrap the given text to the given width.

    Args:
        text (str): The text to wrap.
        width (int): The width to wrap the text to.

    Returns:
        List[str]: A list of strings, each representing a line of the wrapped text.
    """
    return textwrap.wrap(text, width);

def wrap_text_with_indent(text: str, width: int, indent: int) -> List[str]:
    """Wrap the given text to the given width, with the given indent.

    Args:
        text (str): The text to wrap.
        width (int): The width to wrap the text to.
        indent (int): The number of spaces to indent each line.

    Returns:
        List[str]: A list of strings, each representing a line of the wrapped text.
    """
    return textwrap.wrap(text, width, initial_indent=' ' * indent, subsequent_indent=' ' * indent);

def wrap_text_with_indent_and_prefix(text: str, width: int, indent: int, prefix: str) -> List[str]:
    """Wrap the given text to the given width, with the given indent and prefix.

    Args:
        text (str): The text to wrap.
        width (int): The width to wrap the text to.
        indent (int): The number of spaces to indent each line.
        prefix (str): The prefix to add to each line.

    Returns:
        List[str]: A list of strings, each representing a line of the wrapped text.
    """
    return textwrap.wrap(text, width, initial_indent=' ' * indent + prefix, subsequent_indent=' ' * indent + prefix);

def getTags(tags: List[str]) -> str:
    """Get a string representation of the given list of tags.

    Args:
        tags (List[str]): A list of tags.

    Returns:
        str: A string representation of the tags.
    """
    return ' '.join(['#' + tag for tag in tags]);