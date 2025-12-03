"""
Coordinate Parser for DeepSeek OCR
Parses grounding boxes from model output and scales coordinates
Extracted from backend/main.py (lines 167-244)
"""

import re
from typing import List, Dict, Any


# Match a full detection block and capture the coordinates as the entire list expression
# Examples of captured coords (including outer brackets):
#  - [[312, 339, 480, 681]]
#  - [[504, 700, 625, 910], [771, 570, 996, 996]]
#  - [[110, 310, 255, 800], [312, 343, 479, 680], ...]
# Using a greedy bracket capture ensures we include all inner lists up to the last ']' before </|det|>
DET_BLOCK = re.compile(
    r"<\|ref\|>(?P<label>.*?)<\|/ref\|>\s*<\|det\|>\s*(?P<coords>\[.*\])\s*<\|/det\|>",
    re.DOTALL,
)


def clean_grounding_text(text: str) -> str:
    """Remove grounding tags from text for display, keeping labels

    Args:
        text: Raw model output with grounding tags

    Returns:
        Cleaned text with tags removed
    """
    # Replace <|ref|>label<|/ref|><|det|>[...any nested lists...]<|/det|> with just the label
    cleaned = re.sub(
        r"<\|ref\|>(.*?)<\|/ref\|>\s*<\|det\|>\s*\[.*\]\s*<\|/det\|>",
        r"\1",
        text,
        flags=re.DOTALL,
    )
    # Also remove any standalone grounding tags
    cleaned = re.sub(r"<\|grounding\|>", "", cleaned)
    return cleaned.strip()


def parse_detections(text: str, image_width: int, image_height: int) -> List[Dict[str, Any]]:
    """Parse grounding boxes from text and scale from 0-999 normalized coords to actual image dimensions

    Handles both single and multiple bounding boxes:
    - Single: <|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2]]<|/det|>
    - Multiple: <|ref|>label<|/ref|><|det|>[[x1,y1,x2,y2], [x1,y1,x2,y2], ...]<|/det|>

    Args:
        text: Raw model output with detection tags
        image_width: Original image width in pixels
        image_height: Original image height in pixels

    Returns:
        List of dictionaries with 'label' and 'box' keys
        box format: [x1, y1, x2, y2] in actual pixel coordinates
    """
    boxes: List[Dict[str, Any]] = []
    for m in DET_BLOCK.finditer(text or ""):
        label = m.group("label").strip()
        coords_str = m.group("coords").strip()

        print(f"🔍 DEBUG: Found detection for '{label}'")
        print(f"📦 Raw coords string (with brackets): {coords_str}")

        try:
            import ast

            # Parse the full bracket expression directly (handles single and multiple)
            parsed = ast.literal_eval(coords_str)

            # Normalize to a list of lists
            if (
                isinstance(parsed, list)
                and len(parsed) == 4
                and all(isinstance(n, (int, float)) for n in parsed)
            ):
                # Single box provided as [x1,y1,x2,y2]
                box_coords = [parsed]
                print("📦 Single box (flat list) detected")
            elif isinstance(parsed, list):
                box_coords = parsed
                print(f"📦 Boxes detected: {len(box_coords)}")
            else:
                raise ValueError("Unsupported coords structure")

            # Process each box
            for idx, box in enumerate(box_coords):
                if isinstance(box, (list, tuple)) and len(box) >= 4:
                    # Scale from 0-999 normalized coords to actual pixels
                    x1 = int(float(box[0]) / 999 * image_width)
                    y1 = int(float(box[1]) / 999 * image_height)
                    x2 = int(float(box[2]) / 999 * image_width)
                    y2 = int(float(box[3]) / 999 * image_height)
                    print(f"  Box {idx+1}: {box} → [{x1}, {y1}, {x2}, {y2}]")
                    boxes.append({"label": label, "box": [x1, y1, x2, y2]})
                else:
                    print(f"  ⚠️ Skipping invalid box: {box}")
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            continue

    print(f"🎯 Total boxes parsed: {len(boxes)}")
    return boxes
