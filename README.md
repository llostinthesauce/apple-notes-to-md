# Apple Notes to Markdown (apple-notes-to-md)

A robust utility for exporting your macOS Apple Notes into cleanly formatted Markdown (`.md`) files. Designed for **Second Brain** systems, **LLM RAG ingestion**, and archival purposes.

## 🚀 Purpose
Apple Notes is a great capturing tool, but its data is locked in a proprietary database. `apple-notes-to-md` unlocks your notes by converting them into standard Markdown files while preserving:
- Folder structures and Account groupings
- Native formatting (lists, headers, etc.)
- Metadata (Creation Date, Modification Date)

## 🛠 How it Works
The tool uses a combination of **Native AppleScript** and macOS's **`textutil`** engine. 
- **AppleScript** reliably iterates through your notes one-by-one to avoid the memory/hanging issues common with bulk exports.
- **`textutil`** ensures that Apple's internal HTML representation is accurately converted to clean plain text/Markdown.

## 📋 Prerequisites
- **macOS** (Required for AppleScript/Notes app access)
- **Python 3.x**

## 🏃 Usage
1. **Clone the repository:**
   ```bash
   git clone git@github.com:llostinthesauce/apple-notes-to-md.git
   cd apple-notes-to-md
   ```
2. **Run the export script:**
   ```bash
   python3 export_notes.py
   ```
3. **Grant Permissions:** 
   When prompted, click **OK** to allow Terminal/Python to access your Apple Notes.

4. **Results:**
   Your notes will be exported to the `Exported_Notes/` directory, organized by **Account > Folder > Note.md**.

## 🧠 LLM / RAG Ready
Each exported `.md` file includes a YAML-style header with the note's original title and timestamps, making it ideal for ingestion into local LLMs or RAG pipelines.
