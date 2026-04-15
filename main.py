"""Document-to-Markdown batch converter.

Recursively scans a source directory for supported files (PDFs and office
documents) and converts each one to Markdown.  The resulting Markdown files
are written into an ``Extracts`` folder that mirrors the original directory
structure.

Supported formats
-----------------
- **PDF** — via pymupdf4llm (with a plain PyMuPDF fallback).
- **Office** — .docx, .doc, .xlsx, .xls, .pptx, .ppt via markitdown.

Features
--------
- Preserves tables, headers, and reading order where possible.
- Extracts embedded images from PDFs into per-document ``<stem>_images/`` folders.
- Prepends a Wikilink ``[[OriginalFile.ext]]`` at the top of every Markdown
  file for easy back-referencing (e.g. in Obsidian).
- Automatically skips the output folder to avoid re-processing.

Usage
-----
    python main.py [source_dir]

If *source_dir* is omitted the current working directory is used.

Dependencies
------------
- pymupdf4llm   (PDF converter)
- pymupdf       (PDF engine & fallback text extraction)
- pymupdf_layout (optional, improves page-layout analysis)
- markitdown    (office-document converter)
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from office_converter import SUPPORTED_EXTENSIONS as OFFICE_EXTENSIONS
from office_converter import convert_office
from pdf_converter import SUPPORTED_EXTENSIONS as PDF_EXTENSIONS
from pdf_converter import convert_pdf

LOGGER = logging.getLogger(__name__)

OUTPUT_DIR_NAME = "Extracts"


def build_output_path(source_root: Path, output_root: Path, file_path: Path) -> Path:
    relative_path = file_path.relative_to(source_root)
    output_dir = output_root / relative_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{file_path.stem}.md"


def convert_tree(source_root: Path) -> dict[str, int]:
    output_root = source_root / OUTPUT_DIR_NAME
    output_root.mkdir(parents=True, exist_ok=True)
    output_root_resolved = output_root.resolve()

    counts: dict[str, int] = {"pdf": 0, "office": 0, "skipped": 0}

    for root, dirs, files in os.walk(source_root):
        root_path = Path(root)
        dirs[:] = [
            directory
            for directory in dirs
            if (root_path / directory).resolve() != output_root_resolved
        ]

        for filename in files:
            file_path = root_path / filename
            ext = file_path.suffix.lower()

            if ext in PDF_EXTENSIONS:
                output_path = build_output_path(source_root, output_root, file_path)
                try:
                    convert_pdf(file_path, output_path)
                    counts["pdf"] += 1
                except Exception as exc:
                    LOGGER.error("Failed to convert PDF %s: %s", file_path, exc)

            elif ext in OFFICE_EXTENSIONS:
                output_path = build_output_path(source_root, output_root, file_path)
                try:
                    convert_office(file_path, output_path)
                    counts["office"] += 1
                except Exception as exc:
                    LOGGER.error("Failed to convert office file %s: %s", file_path, exc)

            else:
                LOGGER.info("Skipped %s (unsupported extension: %s)", file_path, ext)
                counts["skipped"] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PDFs and office documents in a directory tree to Markdown.",
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    source_root = Path(args.source_dir).resolve()
    if not source_root.is_dir():
        raise SystemExit(f"Source directory not found: {source_root}")

    counts = convert_tree(source_root)
    total = counts["pdf"] + counts["office"]
    LOGGER.info(
        "Converted %d file(s) (%d PDF, %d office, %d skipped). Output is in %s",
        total,
        counts["pdf"],
        counts["office"],
        counts["skipped"],
        source_root / OUTPUT_DIR_NAME,
    )


if __name__ == "__main__":
    main()
