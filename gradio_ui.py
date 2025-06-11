# gradio_ui.py
import gradio as gr
import os
from dotenv import load_dotenv

# Load environment variables (like your GOOGLE_API_KEY)
load_dotenv()

# Import the function that runs your LangGraph app
from app import get_meeting_summary_report

# --- Define the Gradio App using gr.Blocks ---
# This is a more flexible way to design your UI layout

with gr.Blocks(title="Intelligent Meeting Summarizer") as demo:
    gr.Markdown("# Intelligent Meeting Summarizer")
    gr.Markdown("Paste your meeting transcript below to get a summarized report with key decisions and action items using a multi-agent AI system.")

    # Input Section (will be at the top)
    # Using gr.Column() ensures its contents stack vertically
    with gr.Column():
        transcript_input = gr.Textbox(
            lines=5,
            label="Paste Meeting Transcript Here",
            placeholder="e.g., John: Let's discuss the Q3 budget. Sarah: I'll send the report next Wednesday..."
        )
        submit_button = gr.Button("Generate Report")

    # Output Section (will be below the input section)
    output_report = gr.Markdown(
        label="Generated Meeting Report"
    )
    submit_button.click(
        fn=get_meeting_summary_report, # The function to call
        inputs=transcript_input,       # The input component(s)
        outputs=output_report,         # The output component(s)
        api_name="summarize"           # Optional: gives an API endpoint name
    )

# Launch the Gradio app
if __name__ == "__main__":
    print("Launching Gradio interface locally...")
    demo.launch(
        share=False, # Set to True for a temporary public shareable link
        inbrowser=True # Automatically open in your default browser
    )
    print("Gradio interface launched. Check your browser.")