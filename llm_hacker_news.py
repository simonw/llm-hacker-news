import llm
import html
import httpx
import json
import re
from typing import Dict, List, Any


@llm.hookimpl
def register_fragment_loaders(register):
    register("hn", hacker_news_loader)


def hacker_news_loader(argument: str) -> llm.Fragment:
    try:
        response = httpx.get(f"https://hn.algolia.com/api/v1/items/{argument}")
        response.raise_for_status()
        data = response.json()
    except Exception as ex:
        raise ValueError(f"Could not load Hacker News {argument}: {str(ex)}")
    return llm.Fragment(
        process_hn_comments(data),
        source=f"https://news.ycombinator.com/item?id={argument}",
    )


def convert_hn_to_thread_path(
    json_data: Dict[str, Any], path: str = "", result: List[str] = None
) -> List[str]:
    """
    Convert Hacker News JSON hierarchy to thread path notation.

    Args:
        json_data: The JSON data from HN API
        path: Current thread path (used in recursion)
        result: Accumulator for formatted comments

    Returns:
        List of formatted comments in thread path notation
    """
    if result is None:
        result = []

    # Handle root node
    if not path:
        # Root node needs special handling as it might not be in the standard format
        if "text" in json_data:  # It's a comment
            comment_text = clean_html_content(json_data.get("text", ""))
            result.append(f"[1] {json_data.get('author', 'Anonymous')}: {comment_text}")
            current_path = "1"
        else:  # It's a story or top-level item
            title = json_data.get("title", "")
            result.append(f"[1] {json_data.get('author', 'Anonymous')}: {title}")
            current_path = "1"
    else:
        current_path = path

    # Process children recursively
    if "children" in json_data and json_data["children"]:
        for i, child in enumerate(json_data["children"], 1):
            child_path = f"{current_path}.{i}" if current_path else f"{i}"

            # Handle the comment text, unescape HTML entities and clean HTML
            comment_text = clean_html_content(child.get("text", ""))

            result.append(
                f"[{child_path}] {child.get('author', 'Anonymous')}: {comment_text}"
            )

            # Process this child's children
            convert_hn_to_thread_path(child, child_path, result)

    return result


def clean_html_content(text: str) -> str:
    """
    Clean HTML content by unescaping entities and removing HTML tags.

    Args:
        text: HTML text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # First unescape HTML entities
    text = html.unescape(text)

    # Replace paragraph tags with newlines
    text = text.replace("<p>", "\n").replace("</p>", "")

    # Remove link tags but keep the link text
    text = re.sub(r"<a\s+href=[^>]*>(.*?)</a>", r"\1", text)

    # Remove all other HTML tags
    text = re.sub(r"<[^>]*>", "", text)

    return text


def process_hn_comments(json_str: str) -> str:
    """
    Process the JSON string from HN API and return thread path notation.

    Args:
        json_str: JSON string from HN API

    Returns:
        Formatted string with thread path notation
    """
    try:
        json_data = json.loads(json_str) if isinstance(json_str, str) else json_str
        formatted_comments = convert_hn_to_thread_path(json_data)
        return "\n\n".join(formatted_comments)
    except Exception as e:
        return f"Error processing JSON: {str(e)}"
