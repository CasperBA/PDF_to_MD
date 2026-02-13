"""PDF-to-Markdown batch converter.

Recursively scans a source directory for PDF files and converts each one to
Markdown using pymupdf4llm (with a plain PyMuPDF fallback). The resulting
Markdown files are written into a ``PDF_Extracts`` folder that mirrors the
original directory structure.

Features
--------
- Preserves tables, headers, and reading order via pymupdf4llm.
- Extracts embedded images into per-document ``<stem>_images/`` folders.
- Prepends a Wikilink ``[[OriginalFile.pdf]]`` at the top of every Markdown
  file for easy back-referencing (e.g. in Obsidian).
- Automatically skips the output folder to avoid re-processing.

Usage
-----
    python main.py [source_dir]

If *source_dir* is omitted the current working directory is used.

Dependencies
------------
- pymupdf4llm  (primary converter)
- pymupdf      (PDF engine & fallback text extraction)
- pymupdf_layout (optional, improves page-layout analysis)
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path


LOGGER = logging.getLogger(__name__)


def extract_markdown(pdf_path: Path, image_dir: Path) -> str:
    try:
        from pymupdf4llm import to_markdown
    except ImportError:
        to_markdown = None

    if to_markdown is not None:
        try:
            image_dir.mkdir(parents=True, exist_ok=True)
            return to_markdown(
                str(pdf_path),
                write_images=True,
                image_path=str(image_dir),
            ).strip()
        except Exception as exc:
            LOGGER.warning(
                "pymupdf4llm failed for %s (%s). Falling back to PyMuPDF text.",
                pdf_path,
                exc,
            )

    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependencies. Install pymupdf4llm and pymupdf to enable extraction."
        ) from exc

    with fitz.open(pdf_path) as doc:
        pages = [page.get_text("text").rstrip() for page in doc]

    return "\n\n".join(page for page in pages if page).strip()


def build_output_path(source_root: Path, output_root: Path, pdf_path: Path) -> Path:
    relative_path = pdf_path.relative_to(source_root)
    output_dir = output_root / relative_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{pdf_path.stem}.md"


def convert_tree(source_root: Path) -> int:
    output_root = source_root / "PDF_Extracts"
    output_root.mkdir(parents=True, exist_ok=True)
    output_root_resolved = output_root.resolve()

    converted = 0
    for root, dirs, files in os.walk(source_root):
        root_path = Path(root)
        dirs[:] = [
            directory
            for directory in dirs
            if (root_path / directory).resolve() != output_root_resolved
        ]

        for filename in files:
            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = root_path / filename
            output_path = build_output_path(source_root, output_root, pdf_path)
            image_dir = output_path.parent / f"{pdf_path.stem}_images"

            markdown_body = extract_markdown(pdf_path, image_dir)
            wikilink = f"[[{pdf_path.name}]]"
            content = f"{wikilink}\n\n{markdown_body}\n" if markdown_body else f"{wikilink}\n"

            output_path.write_text(content, encoding="utf-8")
            converted += 1
            LOGGER.info("Wrote %s", output_path)

    return converted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PDFs in a directory tree to Markdown with mirrored output structure.",
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="Root directory to scan for PDFs (default: current directory).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    source_root = Path(args.source_dir).resolve()
    if not source_root.is_dir():
        raise SystemExit(f"Source directory not found: {source_root}")

    converted = convert_tree(source_root)
    LOGGER.info("Converted %s PDF(s). Output is in %s", converted, source_root / "PDF_Extracts")


if __name__ == "__main__":
    main()
