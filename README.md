# pdf-md

Batch-convert PDFs and office documents to Markdown while preserving tables, headers, and images.

## Features

- **Recursive scanning** — walks all directories and subdirectories of a source folder.
- **Structure mirroring** — outputs are written to an `Extracts/` folder that mirrors the original directory layout.
- **Multi-format support** — converts PDFs, Word documents, Excel spreadsheets, and PowerPoint presentations.
- **Table & header preservation** — uses [pymupdf4llm](https://pypi.org/project/pymupdf4llm/) for high-fidelity PDF conversion and [markitdown](https://pypi.org/project/markitdown/) for office documents.
- **Image extraction** — embedded images from PDFs are saved to per-document `<name>_images/` folders and referenced in the Markdown.
- **Wikilink header** — each Markdown file starts with `[[OriginalFile.ext]]` for easy back-referencing (e.g. in Obsidian).
- **Fallback** — if pymupdf4llm fails for a PDF, plain text is extracted via PyMuPDF.

## Supported Formats

| Extension | Type                | Converter             |
| -----------| ---------------------| -----------------------|
| `.pdf`    | PDF                 | pymupdf4llm / PyMuPDF |
| `.docx`   | Word                | markitdown            |
| `.doc`    | Word (legacy)       | markitdown            |
| `.xlsx`   | Excel               | markitdown            |
| `.xls`    | Excel (legacy)      | markitdown            |
| `.pptx`   | PowerPoint          | markitdown            |
| `.ppt`    | PowerPoint (legacy) | markitdown            |

## Installation

Requires **Python 3.13+**.

```bash
# Clone the repository
git clone <repo-url>
cd pdf-md

# Install dependencies (using uv)
uv sync
```

### Dependencies

| Package          | Purpose                                 |
| ------------------| -----------------------------------------|
| `pymupdf4llm`    | Primary PDF → Markdown converter        |
| `pymupdf`        | PDF engine (installed with pymupdf4llm) |
| `pymupdf_layout` | Optional, improves page-layout analysis |
| `markitdown`     | Office document → Markdown converter    |

## Usage

```bash
python main.py [source_dir]
```

- **`source_dir`** — root directory to scan for supported files. Defaults to the current directory if omitted.

### Example

```bash
python main.py "C:\Users\me\Documents\Reports"
```

This produces:

```
Reports/
  Extracts/
    subdir/
      Report.md
      Report_images/
        img-0001.png
      Meeting_Notes.md
    AnnualReview.md
    AnnualReview_images/
        img-0001.png
    Budget.md
```

Each generated `.md` file starts with a Wikilink to the original document:

```markdown
[[Report.pdf]]

# Report Title
...
```

## Project Structure

| File                  | Purpose                                      |
| --------------------- | -------------------------------------------- |
| `main.py`             | Orchestrator — walks directory, dispatches files |
| `pdf_converter.py`    | PDF → Markdown (pymupdf4llm / PyMuPDF)      |
| `office_converter.py` | Office → Markdown (markitdown)               |