# gradio_ui.py
import gradio as gr
import os
from dotenv import load_dotenv
import pypdf
import time # Remove this if you no longer need time.sleep() for other reasons

# Load environment variables
load_dotenv()

# Import the function that runs your LangGraph app
from app import get_meeting_summary_report

# --- Helper function to read content from uploaded file ---
def read_file_content(file_obj) -> str:
    """Reads content from an uploaded file object (txt or pdf)."""
    if file_obj is None:
        return ""
    file_path = file_obj.name
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".txt":
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            gr.Warning(f"Error reading text file: {e}")
            return f"Error reading text file: {e}"
    elif file_extension == ".pdf":
        try:
            reader = pypdf.PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
            return content
        except Exception as e:
            gr.Warning(f"Could not read PDF file. Make sure it's not an image-based PDF or corrupted: {e}")
            return f"Error reading PDF: {e}"
    else:
        gr.Warning(f"Unsupported file type: {file_extension}. Please upload a .txt or .pdf file.")
        return ""

# --- Unified function to handle both file and text input (retains gr.Progress if you still want it) ---
def unified_summarize_input(uploaded_file, pasted_text, progress=gr.Progress()):
    """
    This function handles both file and text input,
    processes the correct input, and updates the progress bar (if gr.Progress works).
    """
    progress(0, desc="Initializing...")

    transcript_text = ""

    if uploaded_file is not None:
        progress(0.05, desc="Reading uploaded file...")
        transcript_text = read_file_content(uploaded_file)
        if not transcript_text:
            progress(1.0, desc="Error")
            return "No content found in the uploaded file, or an error occurred during reading/unsupported file type. Please try again."
    elif pasted_text and pasted_text.strip() != "":
        transcript_text = pasted_text
        progress(0.05, desc="Processing pasted text...")
    else:
        progress(1.0, desc="Error")
        return "Please either upload a transcript file or paste text into the textbox."

    progress(0.2, desc="Starting AI summarization pipeline...")

    try:
        report = get_meeting_summary_report(transcript_text)
        # REMOVED: time.sleep(3) that was added for debugging
        progress(0.9, desc="Finalizing report...")
        return report
    except Exception as e:
        progress(1.0, desc="Error")
        gr.Warning(f"An error occurred during summarization: {e}")
        return f"An unexpected error occurred during summarization: {str(e)}"
    finally:
        progress(1.0, desc="Done.")

# --- REMOVED: show_spinner() and hide_spinner() functions ---

# --- Function to create and return the Gradio Blocks app ---
def create_gradio_blocks_app():
    """
    Creates and returns the Gradio Blocks app instance.
    """
    with gr.Blocks(title="Intelligent Meeting Summarizer") as demo:
        # REMOVED: demo.css for the spinner
        # REMOVED: gr.HTML for CSS if it was there

        gr.Markdown("# 🚀 Intelligent Meeting Summarizer AI")
        gr.Markdown("Choose your preferred input method: upload a file or paste your meeting transcript directly.")

        with gr.Column():
            with gr.Tabs():
                with gr.TabItem("Upload File"):
                    transcript_file_input = gr.File(
                        label="Upload Meeting Transcript (.txt or .pdf)",
                        file_types=[".txt", ".pdf"],
                        type="filepath"
                    )
                with gr.TabItem("Paste Text"):
                    transcript_text_input = gr.Textbox(
                        lines=5,
                        label="Paste Meeting Transcript Here",
                        placeholder="e.g., John: Let's discuss the Q3 budget. Sarah: I'll send the report next Wednesday..."
                    )
            
            submit_button = gr.Button("Generate Report")
            
            # REMOVED: spinner = gr.HTML(...)

        output_report = gr.Markdown(
            label="Generated Meeting Report"
        )

        # Updated Button click: Direct call to unified_summarize_input
        submit_button.click(
            fn=unified_summarize_input,
            inputs=[transcript_file_input, transcript_text_input],
            outputs=output_report,
            api_name="summarize",
            # If gr.Progress() also doesn't visually work, you can try
            # show_progress="full" here again, though you mentioned it didn't work previously.
            # No need to add it if you're happy without an explicit spinner.
        )
    return demo

# --- Main execution block for local testing ---
if __name__ == "__main__":
    print("Launching Gradio interface locally...")
    app = create_gradio_blocks_app()
    app.launch(
        share=False,
        inbrowser=True
    )
    print("Gradio interface launched. Check your browser.")