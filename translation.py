import pytesseract
from PIL import Image
from pathlib import Path
import argparse

SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}


def extract_text(image_path: str, language: str = "guj") -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image_path: Path to the image file (TIF, PNG, JPG, etc.)
        language: Tesseract language code (default: 'guj' for Gujarati)

    Returns:
        Extracted text as a string.
    """
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=language)
    return text


def extract_text_from_image(image: Image.Image, language: str = "guj") -> str:
    """Extract text from a PIL Image using Tesseract OCR."""
    return pytesseract.image_to_string(image, lang=language)


def save_text(text: str, output_path: str) -> None:
    """Save extracted text to a file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Text saved to: {output_path}")


def process_folder(input_dir: Path, output_root: Path, language: str = "guj") -> None:
    """Translate all supported images in a folder and save text copies."""
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a folder: {input_dir}")

    output_dir = output_root / input_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [
        p
        for p in sorted(input_dir.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print(f"No supported image files found in {input_dir}")
        return

    for file_path in files:
        print(f"Processing {file_path.name}...")
        text = extract_text(str(file_path), language)
        output_file = output_dir / f"{file_path.stem}.txt"
        save_text(text, str(output_file))

    print(f"Finished. Translated files saved to: {output_dir}")