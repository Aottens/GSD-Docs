# Corporate Style Reference Document (huisstijl.docx)

## Purpose

The `huisstijl.docx` file is a Pandoc reference document that defines corporate styling for exported SDS documents. It controls fonts, headings, table styles, headers, footers, and other DOCX formatting.

## Creating huisstijl.docx

### Option 1: Generate with Pandoc (Recommended)

If you have Pandoc 3.9+ installed:

```bash
# Generate default reference document
pandoc --print-default-data-file reference.docx -o gsd-docs-industrial/references/huisstijl.docx
```

Then customize the generated file in Microsoft Word with the corporate styles described below.

### Option 2: Create from Scratch in Word

Create a new DOCX file named `huisstijl.docx` in this directory and apply the styles described below.

## Required Style Customizations

Open `huisstijl.docx` in Microsoft Word and customize these styles:

### Heading Styles

- **Heading 1**
  - Font: 16pt bold
  - Color: Dark blue (#003366)
  - Spacing after: 12pt

- **Heading 2**
  - Font: 14pt bold
  - Color: Dark blue (#003366)
  - Spacing after: 10pt

- **Heading 3**
  - Font: 12pt bold
  - Color: Dark blue (#003366)
  - Spacing after: 8pt

### Body Text

- **Normal**
  - Font: 11pt Calibri
  - Line spacing: 1.15
  - Spacing after: 6pt

### Table Styles

- **Table Grid**
  - Borders: Thin borders on all cells
  - Header row: Light blue background (#DCE6F1)
  - Font: 10pt for cells

### Other Styles

- **Caption**
  - Font: 10pt italic
  - Spacing before: 6pt

### Headers and Footers

Configure the document header with three sections:

- **Left**: Company logo placeholder
- **Center**: Document title
- **Right**: Version number

Configure the document footer with three sections:

- **Left**: Document number
- **Center**: Page number
- **Right**: Date

## Usage

The `/doc:export` command uses this file via Pandoc's `--reference-doc` option:

```bash
pandoc FDS.md -o FDS.docx --reference-doc=gsd-docs-industrial/references/huisstijl.docx
```

If `huisstijl.docx` is missing, the export command will issue a warning and use Pandoc's default styling.

## Installation Check

To verify Pandoc is installed:

```bash
pandoc --version
```

If not installed, download from: https://pandoc.org/installing.html

Minimum version: Pandoc 3.9 or higher
