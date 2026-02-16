# Samuel

A simple terminal code browser with AI-assisted code generation.

## What this project does

This project has two parts:

- `frontend`: a Textual TUI to browse and edit files.
- `bot`: a small Gemini client used to generate code from prompts.

You can open files, edit them, save changes, and ask Gemini to insert generated code at the cursor.

## Requirements

- Python 3.10+
- A Gemini API key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install textual rich pygments google-genai
```

3. Configure your API key:

```bash
cp .env.example .env
```

Then edit `.env` and set:

```dotenv
GEMINI_API_KEY=your_key_here
```

## Run

From the project root:

```bash
python frontend/tui.py [PATH]
```

- If `PATH` is omitted, the app opens the current working directory.
- If `PATH` is provided, it must be an existing directory path.

## Main controls

- `f`: show/hide file tree
- `i`: toggle insert mode
- `escape`: exit insert mode or close request input
- `c`: open code request input (Gemini)
- `v`: toggle selection mode
- `y`: yank selection
- `p`: paste yanked text
- `d`: delete selection
- `s`: save all changed files
- `q`: quit

## Notes

- If no API key is set, AI generation is disabled.
- Generated code is inserted at the current cursor position.
- The app tracks unsaved buffers and writes them with `s`.
