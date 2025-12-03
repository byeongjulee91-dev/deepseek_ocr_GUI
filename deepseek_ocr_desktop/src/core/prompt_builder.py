"""
Prompt Builder for DeepSeek OCR
Builds prompts based on OCR mode and user inputs
Extracted from backend/main.py (lines 100-163)
"""

from typing import Optional, List


def build_prompt(
    mode: str,
    user_prompt: str,
    grounding: bool,
    find_term: Optional[str],
    schema: Optional[str],
    include_caption: bool,
) -> str:
    """Build the prompt based on mode

    Args:
        mode: OCR mode (plain_ocr, describe, find_ref, etc.)
        user_prompt: Custom prompt for freeform mode
        grounding: Enable grounding boxes
        find_term: Term to find (for find_ref mode)
        schema: JSON schema (for kv_json mode)
        include_caption: Add image description

    Returns:
        Formatted prompt string for the model
    """
    parts: List[str] = ["<image>"]
    mode_requires_grounding = mode in {"find_ref", "layout_map", "pii_redact"}
    if grounding or mode_requires_grounding:
        parts.append("<|grounding|>")

    instruction = ""
    if mode == "plain_ocr":
        instruction = "Free OCR."
    elif mode == "markdown":
        instruction = "Convert the document to markdown."
    elif mode == "tables_csv":
        instruction = (
            "Extract every table and output CSV only. "
            "Use commas, minimal quoting. If multiple tables, separate with a line containing '---'."
        )
    elif mode == "tables_md":
        instruction = "Extract every table as GitHub-flavored Markdown tables. Output only the tables."
    elif mode == "kv_json":
        schema_text = schema.strip() if schema else "{}"
        instruction = (
            "Extract key fields and return strict JSON only. "
            f"Use this schema (fill the values): {schema_text}"
        )
    elif mode == "figure_chart":
        instruction = (
            "Parse the figure. First extract any numeric series as a two-column table (x,y). "
            "Then summarize the chart in 2 sentences. Output the table, then a line '---', then the summary."
        )
    elif mode == "find_ref":
        key = (find_term or "").strip() or "Total"
        instruction = f"Locate <|ref|>{key}<|/ref|> in the image."
    elif mode == "layout_map":
        instruction = (
            'Return a JSON array of blocks with fields {"type":["title","paragraph","table","figure"],'
            '"box":[x1,y1,x2,y2]}. Do not include any text content.'
        )
    elif mode == "pii_redact":
        instruction = (
            'Find all occurrences of emails, phone numbers, postal addresses, and IBANs. '
            'Return a JSON array of objects {label, text, box:[x1,y1,x2,y2]}.'
        )
    elif mode == "multilingual":
        instruction = "Free OCR. Detect the language automatically and output in the same script."
    elif mode == "describe":
        instruction = "Describe this image. Focus on visible key elements."
    elif mode == "freeform":
        instruction = user_prompt.strip() if user_prompt else "OCR this image."
    else:
        instruction = "OCR this image."

    if include_caption and mode not in {"describe"}:
        instruction = instruction + "\nThen add a one-paragraph description of the image."

    parts.append(instruction)
    return "\n".join(parts)
