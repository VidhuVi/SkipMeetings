# 🚀 Intelligent Meeting Summarizer AI

## Project Overview

This project develops a cutting-edge multi-agent AI system designed to automatically summarize meeting transcripts. Leveraging the power of Large Language Models (LLMs) and advanced orchestration frameworks, it transforms raw meeting discussions into concise, actionable reports.

### Key Features:

- **Multi-Agent Architecture:** Utilizes specialized AI agents (Preprocessor, Summarizer, Extractor, Reporter) orchestrated by LangGraph for robust, sequential processing.
- **Intelligent Extraction:** Automatically identifies key topics, critical decisions, and actionable items including assignees and deadlines.
- **Structured Output:** Generates reports in a clear, formatted Markdown structure, making information digestible and usable.
- **Web-Based Interface:** Provides an easy-to-use graphical user interface (GUI) built with Gradio for seamless interaction.
- **Flexible Input:** Supports pasting raw text transcripts directly into the UI. (Future: file upload for .txt/.pdf and audio transcription)

## Architecture

The system is built upon a layered architecture:

1.  **Frontend (Gradio):** Provides an interactive web interface for users to input transcripts and view generated reports.
2.  **Orchestration Layer (LangGraph):** Manages the flow and communication between different AI agents, ensuring a coherent and stateful workflow.
    - **`Transcript Preprocessor Agent`**: Cleans the raw input and extracts foundational data like keywords, person names, and time expressions.
    - **`Core Summarizer Agent`**: Generates a high-level executive summary of the meeting.
    - **`Action & Decision Extractor Agent`**: Identifies specific action items (what, who, when) and key decisions, structuring them for clarity.
    - **`Final Reporter Agent`**: Compiles all processed data into a comprehensive Markdown report.
3.  **LLM Layer (Google Gemini 1.5 Flash):** The primary Large Language Model used by the agents for understanding, generating, and structuring text.
4.  **Tools:** Specialized Python functions integrated into agents to perform specific, targeted tasks (e.g., structuring extracted data).

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

1.  **Clone the repository:**

    ```bash
    git clone "https://github.com/VidhuVi/SkipMeetings.git"
    cd meeting_summarizer_ai
    ```

2.  **Create and Activate a Python Virtual Environment (highly recommended):**
    This isolates your project's dependencies from your system Python.

    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    All required Python packages are listed in `requirements.txt`.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Google Gemini API Key:**
    - Go to [Google AI Studio](https://ai.google.dev/).
    - Generate a new API key.
    - Create a file named `.env` in the **root directory** of this project (the same folder as `app.py` and `gradio_ui.py`).
    - Add your API key to the `.env` file like this:
      ```
      GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
      ```
      _(Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual API key. **Do NOT commit your `.env` file to Git!** It's already listed in `.gitignore`.)_

## How to Run

To launch the Gradio web interface and interact with the summarizer:

1.  Ensure your virtual environment is active (see Setup steps).
2.  Run the Gradio application:
    ```bash
    python gradio_ui.py
    ```
3.  A local server will start, and your web browser should automatically open to the Gradio interface (usually `http://127.0.0.1:7860/`).
4.  Paste your meeting transcript into the text area and click "Generate Report".

## Project Status

This project is currently an MVP (Minimum Viable Product) with a fully functional multi-agent backend and an interactive Gradio UI.

## Future Enhancements

- **File Uploads:** Add support for uploading `.txt` and `.pdf` files as input.
- **Audio Transcription:** Integrate Speech-to-Text (STT) services to allow direct audio file input.
- **Advanced Report Options:** Implement options to download the report in different formats (e.g., PDF, DOCX).
- **Error Handling & Feedback:** More robust error reporting and user feedback mechanisms in the UI.
- **Performance Optimization:** Further optimize LLM calls for speed and efficiency.

---
