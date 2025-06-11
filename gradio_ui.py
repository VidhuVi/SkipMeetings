# gradio_ui.py
import gradio as gr
import os
from dotenv import load_dotenv
import pypdf # Make sure this is imported

# Load environment variables
load_dotenv()

# Import the function that runs your LangGraph app
from app import get_meeting_summary_report

# --- Helper function to read content from uploaded file (NO CHANGE) ---
def read_file_content(file_obj) -> str:
    """
    Reads content from an uploaded file object (txt or pdf).
    Gradio's file_obj.name contains the temporary file path.
    """
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

# --- NEW: Unified function to handle both file and text input ---
def unified_summarize_input(uploaded_file, pasted_text):
    """
    This function checks if a file was uploaded or text was pasted,
    then processes the correct input.
    """
    transcript_text = ""

    # Prioritize file upload if present
    if uploaded_file is not None:
        transcript_text = read_file_content(uploaded_file)
        if not transcript_text:
            return "No content found in the uploaded file, or an error occurred during reading/unsupported file type. Please try again."
    # If no file, check pasted text
    elif pasted_text and pasted_text.strip() != "":
        transcript_text = pasted_text
    else:
        return "Please either upload a transcript file or paste text into the textbox."

    # Now call your original summarization function with the extracted text
    return get_meeting_summary_report(transcript_text)


# --- Define the Gradio App using gr.Blocks ---
with gr.Blocks(title="Intelligent Meeting Summarizer") as demo:
    gr.Markdown("# 🚀 Intelligent Meeting Summarizer AI")
    gr.Markdown("Choose your preferred input method: upload a file or paste your meeting transcript directly.")

    # --- Input Section with Tabs ---
    with gr.Column():
        with gr.Tabs(): # Use gr.Tabs for different input options
            with gr.TabItem("Upload File"): # First tab for file upload
                transcript_file_input = gr.File(
                    label="Upload Meeting Transcript (.txt or .pdf)",
                    file_types=[".txt", ".pdf"],
                    type="filepath"
                )
            with gr.TabItem("Paste Text"): # Second tab for text pasting
                transcript_text_input = gr.Textbox(
                    lines=5, # You can adjust this height
                    label="Paste Meeting Transcript Here",
                    placeholder="e.g., John: Let's discuss the Q3 budget. Sarah: I'll send the report next Wednesday..."
                )
        
        submit_button = gr.Button("Generate Report")

    # --- Output Section ---
    output_report = gr.Markdown(
        label="Generated Meeting Report"
    )

    # --- Define the behavior when the button is clicked ---
    # The .click() function now passes BOTH input components
    submit_button.click(
        fn=unified_summarize_input, # Call the new unified input handler
        inputs=[transcript_file_input, transcript_text_input], # Pass both inputs
        outputs=output_report,
        api_name="summarize"
    )

# Launch the Gradio app
if __name__ == "__main__":
    print("Launching Gradio interface locally...")
    demo.launch(
        share=False,
        inbrowser=True
    )
    print("Gradio interface launched. Check your browser.")