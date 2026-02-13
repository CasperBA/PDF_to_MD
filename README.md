# pdf-md

Batch-convert PDFs to Markdown while preserving tables, headers, and images.

## Features

- **Recursive scanning** — walks all directories and subdirectories of a source folder.
- **Structure mirroring** — outputs are written to a `PDF_Extracts/` folder that mirrors the original directory layout.
- **Table & header preservation** — uses [pymupdf4llm](https://pypi.org/project/pymupdf4llm/) for high-fidelity conversion.
- **Image extraction** — embedded images are saved to per-document `<name>_images/` folders and referenced in the Markdown.
- **Wikilink header** — each Markdown file starts with `[[OriginalFile.pdf]]` for easy back-referencing (e.g. in Obsidian).
- **Fallback** — if pymupdf4llm fails for a file, plain text is extracted via PyMuPDF.

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

| Package          | Purpose                                  |
| ---------------- | ---------------------------------------- |
| `pymupdf4llm`   | Primary PDF → Markdown converter         |
| `pymupdf`       | PDF engine (installed with pymupdf4llm)  |
| `pymupdf_layout` | Optional, improves page-layout analysis |

## Usage

```bash
python main.py [source_dir]
```

- **`source_dir`** — root directory to scan for PDFs. Defaults to the current directory if omitted.

### Example

```bash
python main.py "C:\Users\me\Documents\Reports"
```

This produces:

```
Reports/
  PDF_Extracts/
    subdir/
      Report.md
      Report_images/
        img-0001.png
    AnnualReview.md
    AnnualReview_images/
        img-0001.png
```

Each generated `.md` file starts with a Wikilink to the original PDF:

```markdown
[[Report.pdf]]

# Report Title
...
```