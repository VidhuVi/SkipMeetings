# 🚀 Intelligent Meeting Summarizer AI

## Project Overview

This project develops a cutting-edge multi-agent AI system designed to automatically summarize meeting transcripts. Leveraging the power of Large Language Models (LLMs) and advanced orchestration frameworks, it transforms raw meeting discussions into concise, actionable reports.

### Key Features:

- **Multi-Agent Architecture:** Utilizes specialized AI agents (Preprocessor, Summarizer, Extractor, Reporter) orchestrated by LangGraph for robust, sequential processing.
- **Intelligent Extraction:** Automatically identifies key topics, critical decisions, and actionable items including assignees and deadlines.
- **Structured Output:** Generates reports in a clear, formatted Markdown structure, making information digestible and usable.
- **Versatile Input:** Provides a web-based interface (Gradio) allowing users to either upload `.txt` or `.pdf` files, or directly paste meeting transcripts.

## Architecture

The system is built upon a layered architecture designed for modularity and scalability:

1.  **Frontend (Gradio UI):** Provides an interactive web interface for users to input transcripts and view generated reports. It's wrapped within a FastAPI application for robust deployment.
2.  **Web Server (FastAPI):** A lightweight and fast Python web framework that serves the Gradio UI and can be extended with additional API endpoints. This acts as the main entry point for the deployed application.
3.  **Orchestration Layer (LangGraph):** Manages the flow and communication between different AI agents, ensuring a coherent and stateful workflow.
    - **`Transcript Preprocessor Agent`**: Cleans the raw input and extracts foundational data like keywords, person names, and time expressions.
    - **`Core Summarizer Agent`**: Generates a high-level executive summary of the meeting.
    - **`Action & Decision Extractor Agent`**: Identifies specific action items (what, who, when) and key decisions, structuring them for clarity.
    - **`Final Reporter Agent`**: Compiles all processed data into a comprehensive Markdown report.
4.  **LLM Layer (Google Gemini 1.5 Flash):** The primary Large Language Model used by the agents for understanding, generating, and structuring text.
5.  **Tools:** Specialized Python functions integrated into agents to perform specific, targeted tasks (e.g., structuring extracted data).
6.  **Containerization (Docker):** The application is containerized using Docker, allowing for consistent and reproducible deployment across different environments.

## 🌐 Deployed Project

The Intelligent Meeting Summarizer is deployed as a web service using **Render** and is accessible publicly.

**Access the Live Application Here:**
[https://skipmeetings.onrender.com/gradio](https://skipmeetings.onrender.com/gradio)

## Setup and Installation (Local Development)

Follow these steps to set up and run the project on your local machine for development.

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/VidhuVi/SkipMeetings.git](https://github.com/VidhuVi/SkipMeetings.git)
    cd SkipMeetings
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
    - Create a file named `.env` in the **root directory** of this project (the same folder as `app.py`, `gradio_ui.py`, and `main.py`).
    - Add your API key to the `.env` file like this:
      ```
      GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
      ```
      _(Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual API key. **Do NOT commit your `.env` file to Git!** It's already listed in `.gitignore`.)_

## How to Run (Local)

You have two options to run the application locally:

1.  **Run the FastAPI server (recommended for local testing that mirrors deployment):**
    This will start the Uvicorn server, hosting both the FastAPI root endpoint and the Gradio UI.

    ```bash
    # Ensure your virtual environment is active
    uvicorn main:app --host 0.0.0.0 --port 7860 --reload
    ```

    _(The `--reload` flag is useful during development to automatically restart the server on code changes. You can omit it for stable testing)._
    Access the Gradio UI in your browser at `http://127.0.0.1:7860/gradio`.

2.  **Run the Gradio app directly (for pure Gradio UI development):**
    This will only start the Gradio UI without the FastAPI wrapper.
    ```bash
    # Ensure your virtual environment is active
    python gradio_ui.py
    ```
    Access the Gradio UI in your browser at the URL provided in your terminal (usually `http://127.0.0.1:7860`).

## Project Status

This project is currently an MVP (Minimum Viable Product) with a fully functional multi-agent backend and an interactive Gradio UI, deployed as a web service.

## Future Enhancements

- **Advanced Report Options:** Implement options to download the report in different formats (e.g., PDF, DOCX).
- **Audio Transcription:** Integrate Speech-to-Text (STT) services to allow direct audio file input.
- **User Authentication:** Add basic user login/session management for more complex use cases.
- **Error Handling & Feedback:** More robust error reporting and user feedback mechanisms in the UI.
- **Performance Optimization:** Further optimize LLM calls for speed and efficiency.
- **Testing Suite:** Implement unit and integration tests for the multi-agent system.

---
