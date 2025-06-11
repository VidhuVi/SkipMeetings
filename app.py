# app.py
import json
from typing import TypedDict, List, Dict, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
import time
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()

# Ensure API key is set
# if "GOOGLE_API_KEY" not in os.environ:
#     raise ValueError("GOOGLE_API_KEY environment variable not set. Please ensure you have a .env file with GOOGLE_API_KEY='YOUR_API_KEY'")

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

# AgentState 
class AgentState(TypedDict):
    raw_transcript: str
    cleaned_transcript: Optional[str]
    extracted_data: Optional[Dict[str, Union[List[str], str, List[Dict]]]] # Updated to include List[Dict] if needed later, and allows more varied data
    meeting_summary: Optional[str]
    action_items: Optional[List[Dict[str, str]]]
    key_decisions: Optional[List[Dict[str, str]]]
    final_report: Optional[str]
    next_node: Optional[str]

class ActionItem(BaseModel):
    what: str = Field(description="A concise summary of the action to be done.")
    who: str = Field(description="The person responsible for the action. Use 'N/A' if not identified.")
    when: str = Field(description="The deadline or timeline for the action. Use 'N/A' if not identified.")

class Decision(BaseModel):
    decision: str = Field(description="The key decision made.")
    category: str = Field(description="The category of the decision (e.g., 'General', 'Strategic', 'Operational', 'Technical').")

class AllActions(BaseModel):
    action_items: List[ActionItem] = Field(description="A list of all identified action items.")

class AllDecisions(BaseModel):
    key_decisions: List[Decision] = Field(description="A list of all identified key decisions.")
# ------------------------------------------------------------------------------TOOLS-------------------------------------------------------------------------------------------------------------
@tool
def extract_keywords(text: str) -> List[str]:
    """
    Extracts a list of key terms and phrases from the provided text.
    A good tool to identify the most important subjects discussed.
    """
    prompt = f"Identify and list the 5-10 most important keywords or key phrases from the following meeting transcript segment, separated by commas. Focus on nouns and significant concepts, do not include numbers: \n\nTEXT: {text}\n\nKEYWORDS:"
    response = llm.invoke([HumanMessage(content=prompt)])
    # Basic parsing: split by comma, strip whitespace, remove empty strings
    keywords = [k.strip() for k in response.content.split(',') if k.strip()]
    return keywords

@tool
def extract_person_names(text: str) -> List[str]:
    """
    Extracts a list of proper person names from the provided text.
    Useful for identifying individuals mentioned in the meeting.
    """
    prompt = f"Identify and list all distinct proper person names mentioned in the following text, separated by commas. Only include names of people. \n\nTEXT: {text}\n\nPERSON NAMES:"
    response = llm.invoke([HumanMessage(content=prompt)])
    names = [n.strip() for n in response.content.split(',') if n.strip()]
    return names

@tool
def extract_time_expressions(text: str) -> List[str]:
    """
    Extracts any explicit or implied time-related expressions (dates, deadlines, durations)
    from the provided text.
    """
    prompt = f"Identify and list all distinct time-related expressions (e.g., 'next week', 'by Friday', 'on June 15th', 'in two days') from the following text, separated by commas. \n\nTEXT: {text}\n\nTIME EXPRESSIONS:"
    response = llm.invoke([HumanMessage(content=prompt)])
    times = [t.strip() for t in response.content.split(',') if t.strip()]
    return times

def structure_action_item(description: str, assignee: Optional[str] = None, deadline: Optional[str] = None) -> Dict[str, str]:
    """
    Structures a raw action item description into a consistent dictionary format.
    Optionally takes identified assignee and deadline.
    """
    prompt = f"""
    Extract the 'what', 'who', and 'when' fields from the given action item description, and optionally an assignee and deadline.
    If a field is not explicitly present, use "N/A" for 'who' and 'when'.
    The 'what' field should be a very short and concise summary of the task.

    Return ONLY the JSON dictionary. DO NOT include any other text, explanation, or markdown fences (```json).

    Description: "{description}"
    Assignee (if identified): {assignee if assignee else 'N/A'}
    Deadline (if identified): {deadline if deadline else 'N/A'}

    JSON Output Example: {{"what": "send report", "who": "John", "when": "next Wednesday"}}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        # We already have robust parsing in the agent, but ensuring the prompt is strict helps.
        # This parsing is primarily for the *agent's* robust JSON handling.
        # The tool itself should ideally get pure JSON.
        json_str = response.content.strip()
        # Still keep these safety checks, but the goal is for the LLM not to need them
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-len("```")].strip()

        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse action item JSON. LLM output: '{response.content}' Error: {e}")
        # Fallback to a default structure or re-prompt/retry if this happens too often
        return {"what": description, "who": assignee if assignee else "N/A", "when": deadline if deadline else "N/A"}

# app.py (modify your existing structure_decision tool)

def structure_decision(decision_text: str, category: Optional[str] = None) -> Dict[str, str]:
    """
    Structures a raw decision text into a consistent dictionary format.
    Optionally takes a category.
    """
    prompt = f"""
    Extract the 'decision' and 'category' fields from the given decision text, and optionally a suggested category.
    If a category is not provided or clear, use "General".

    Return ONLY the JSON dictionary. DO NOT include any other text, explanation, or markdown fences (```json).

    Decision Text: "{decision_text}"
    Suggested Category (if identified): {category if category else 'N/A'}

    JSON Output Example: {{"decision": "Approved Project Alpha", "category": "Strategic"}}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        json_str = response.content.strip()
        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):].strip()
        if json_str.endswith("```"):
            json_str = json_str[:-len("```")].strip()
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse decision JSON. LLM output: '{response.content}' Error: {e}")
        return {"decision": decision_text, "category": category if category else "General"}
# ------------------------------------------------------------------------------AGENTS-------------------------------------------------------------------------------------------------------------

# --- Final Reporter Agent ---
# app.py (This is your final_reporter_agent function)

def final_reporter_agent(state: AgentState) -> AgentState:
    print("\n--- Executing Final Reporter Agent ---")
    
    # Retrieve all necessary data from the state
    summary = state.get("meeting_summary", "No summary available.")
    action_items = state.get("action_items", [])
    key_decisions = state.get("key_decisions", [])
    extracted_data = state.get("extracted_data", {})
    # Use 'cleaned_transcript' directly for the reference section,
    # as it's the version that has potentially gone through preprocessing.
    cleaned_transcript_content = state.get("cleaned_transcript", "No transcript available.") 

    updated_state = state.copy()

    report_sections = []
    report_sections.append("# Meeting Report\n") # Main title for the report

    # --- 1. Executive Summary ---
    report_sections.append("## 1. Executive Summary\n")
    # Assuming the LLM now formats the summary as a clean numbered list directly.
    # Just append it as is, followed by a newline for spacing.
    report_sections.append(f"{summary}\n") 

    # --- 2. Key Decisions ---
    report_sections.append("## 2. Key Decisions\n")
    if key_decisions:
        for i, decision in enumerate(key_decisions):
            # Format each decision clearly
            report_sections.append(f"- **Decision {i+1}:** {decision.get('decision', 'N/A')}")
            report_sections.append(f"  * Category: {decision.get('category', 'General')}\n") # Newline for spacing after each item
    else:
        report_sections.append("No key decisions identified.\n") # Message if no decisions

    # --- 3. Action Items ---
    report_sections.append("## 3. Action Items\n")
    if action_items:
        for i, item in enumerate(action_items):
            # Format each action item clearly
            report_sections.append(f"- **Action {i+1}:** {item.get('what', 'N/A')}")
            report_sections.append(f"  * Who: {item.get('who', 'N/A')}")
            report_sections.append(f"  * When: {item.get('when', 'N/A')}\n") # Newline for spacing after each item
    else:
        report_sections.append("No action items identified.\n") # Message if no action items

    # --- 4. Supplementary Information ---
    report_sections.append("## 4. Supplementary Information\n")
    
    # Extract and format keywords
    keywords = extracted_data.get("keywords", [])
    if keywords:
        report_sections.append(f"- **Keywords:** {', '.join(keywords)}\n")
    
    # Extract and format person names
    names = extracted_data.get("person_names", [])
    if names:
        report_sections.append(f"- **People Mentioned:** {', '.join(names)}\n")
    
    # Extract and format time expressions
    times = extracted_data.get("time_expressions", [])
    if times:
        report_sections.append(f"- **Time-related Expressions:** {', '.join(times)}\n")

    # --- Full Cleaned Transcript (for reference) ---
    # report_sections.append("\n---\n") # Horizontal rule for visual separation
    # report_sections.append("## Full Cleaned Transcript (for reference)\n")
    # # Clean each line of the transcript by stripping leading/trailing whitespace
    # # This addresses the original transcript's indentation/spacing issues.
    # cleaned_transcript_lines = [line.strip() for line in cleaned_transcript_content.split('\n')]
    # report_sections.append("\n".join(cleaned_transcript_lines)) # Join lines back into a single string

    # Combine all sections into the final report string
    final_report_content = "\n".join(report_sections)
    updated_state["final_report"] = final_report_content

    print("  - Final Report Generated (see full output in final_state for content).")

    return updated_state

# --- Transcript Preprocessor & Data Extractor Agent ---
def transcript_preprocessor_agent(state: AgentState) -> AgentState:
    print("\n--- Executing Transcript Preprocessor Agent ---")
    raw_transcript = state["raw_transcript"]
    updated_state = state.copy()

    # Step 1: Clean the transcript (simple for MVP)
    # For an MVP, "cleaning" can be as simple as just using the raw text as cleaned.
    # Later, you might add normalization, removing boilerplate, etc.
    cleaned_transcript = raw_transcript # For now, just pass it through
    updated_state["cleaned_transcript"] = cleaned_transcript
    print(f"  - Cleaned transcript (passed through for now). Length: {len(cleaned_transcript)} chars.")

    # Step 2: Use tools to extract data
    extracted_keywords_list = extract_keywords.invoke({"text": cleaned_transcript})
    extracted_names_list = extract_person_names.invoke({"text": cleaned_transcript})
    extracted_times_list = extract_time_expressions.invoke({"text": cleaned_transcript})

    # Store extracted data in the state
    updated_state["extracted_data"] = {
        "keywords": extracted_keywords_list,
        "person_names": extracted_names_list,
        "time_expressions": extracted_times_list
    }
    print(f"  - Extracted Keywords: {extracted_keywords_list}")
    print(f"  - Extracted Names: {extracted_names_list}")
    print(f"  - Extracted Time Expressions: {extracted_times_list}")

    return updated_state

# --- Core Summarizer Agent ---
def core_summarizer_agent(state: AgentState) -> AgentState:
    print("\n--- Executing Core Summarizer Agent ---")
    cleaned_transcript = state.get("cleaned_transcript")
    updated_state = state.copy()

    if not cleaned_transcript:
        print("  - Error: No cleaned transcript found for summarization.")
        # You might want to handle this more robustly later (e.g., raise an error, go to a different node)
        return updated_state

    # Prompt for summarization
    # Emphasize conciseness and key points for a meeting summary
    prompt = f"""
    You are an expert meeting summarizer. Your task is to create a concise, high-level summary of the provided meeting transcript.
    Focus on the main topics discussed, key outcomes, and important points relevant to the overall meeting purpose.
    **Format the summary as a clean, numbered list of 3-5 concise bullet points, each starting directly with a number (e.g., "1. Main topic discussed..."). Do NOT use asterisks or any other leading characters.**
    --- MEETING TRANSCRIPT ---
    {cleaned_transcript}
    --- SUMMARY ---
    """
    summary_response = llm.invoke([HumanMessage(content=prompt)])
    summary = summary_response.content
    updated_state["meeting_summary"] = summary

    print(f"  - Generated Summary:\n{summary}")

    return updated_state

# --- Action & Decision Extractor Agent ---
def action_decision_extractor_agent(state: AgentState) -> AgentState:
    print("\n--- Executing Action & Decision Extractor Agent ---")
    cleaned_transcript = state.get("cleaned_transcript")
    updated_state = state.copy()

    if not cleaned_transcript:
        print("  - Error: No cleaned transcript found for extraction.")
        return updated_state

    # IMPORTANT: Use with_structured_output to directly get structured data.
    # This replaces the multiple LLM calls inside your previous @tool definitions.

    # 1. Extract Action Items
    # We pass the Pydantic schema (ActionItem) and get the LLM to directly output it.
    action_extractor_llm = llm.with_structured_output(ActionItem, method="json_mode")
    # For Gemini, "json_mode" usually implies it will return a JSON object that matches
    # the schema, leveraging its function calling capabilities implicitly.

    # Instead of an LLM call per action, let's try to get a list of actions in one go.
    # This requires the LLM to output a list of ActionItem.
    class AllActions(BaseModel):
        action_items: List[ActionItem] = Field(description="A list of all identified action items.")

    action_list_extractor_llm = llm.with_structured_output(AllActions, method="json_mode")

    action_prompt = f"""
    Analyze the following meeting transcript and identify all explicit or implied action items.
    For each action item, extract: 'what' (concise description), 'who' (person responsible, use 'N/A' if not identified), and 'when' (deadline/timeline, use 'N/A' if not identified).

    --- MEETING TRANSCRIPT ---
    {cleaned_transcript}
    """
    
    try:
        # One LLM call to get all structured action items
        extracted_actions_obj = action_list_extractor_llm.invoke([HumanMessage(content=action_prompt)])
        structured_actions = [item.model_dump() for item in extracted_actions_obj.action_items] # Convert Pydantic objects to dicts
    except Exception as e:
        print(f"ERROR: Failed to extract structured action items: {e}")
        print("Falling back to a simpler extraction method for action items.")
        # Fallback to the original, less efficient method if structured output fails badly
        action_prompt_fallback = f"""
        Analyze the following meeting transcript and identify all explicit or implied action items.
        List each action item on a new line.

        --- MEETING TRANSCRIPT ---
        {cleaned_transcript}
        --- ACTION ITEMS ---
        """
        raw_actions_response = llm.invoke([HumanMessage(content=action_prompt_fallback)])
        # Manually parse and create ActionItem dicts (simpler, but less structured)
        raw_actions_list = [item.strip() for item in raw_actions_response.content.split('\n') if item.strip()]
        structured_actions = []
        for raw_action in raw_actions_list:
            # Try to infer some fields, but it's less reliable than direct structured output
            structured_actions.append({
                "what": raw_action,
                "who": "N/A", # Will need further LLM call or regex to parse accurately
                "when": "N/A"
            })
        time.sleep(2) # Add a delay for fallback

    updated_state["action_items"] = structured_actions
    print(f"  - Generated Action Items: {structured_actions}")


    # 2. Extract Key Decisions
    class AllDecisions(BaseModel):
        key_decisions: List[Decision] = Field(description="A list of all identified key decisions.")

    decision_list_extractor_llm = llm.with_structured_output(AllDecisions, method="json_mode")

    decision_prompt = f"""
    Analyze the following meeting transcript and identify all explicit key decisions made.
    For each decision, extract: 'decision' (the main decision text) and 'category' (e.g., 'General', 'Strategic', 'Operational', 'Technical').

    --- MEETING TRANSCRIPT ---
    {cleaned_transcript}
    """
    try:
        # One LLM call to get all structured decisions
        extracted_decisions_obj = decision_list_extractor_llm.invoke([HumanMessage(content=decision_prompt)])
        structured_decisions = [item.model_dump() for item in extracted_decisions_obj.key_decisions] # Convert Pydantic objects to dicts
    except Exception as e:
        print(f"ERROR: Failed to extract structured decisions: {e}")
        print("Falling back to a simpler extraction method for decisions.")
        # Fallback to original, less efficient method
        decision_prompt_fallback = f"""
        Analyze the following meeting transcript and identify all explicit key decisions made.
        List each decision on a new line.

        --- MEETING TRANSCRIPT ---
        {cleaned_transcript}
        --- KEY DECISIONS ---
        """
        raw_decisions_response = llm.invoke([HumanMessage(content=decision_prompt_fallback)])
        raw_decisions_list = [item.strip() for item in raw_decisions_response.content.split('\n') if item.strip()]
        structured_decisions = [{"decision": raw_decision, "category": "General"} for raw_decision in raw_decisions_list]
        time.sleep(2) # Add a delay for fallback


    updated_state["key_decisions"] = structured_decisions
    print(f"  - Generated Key Decisions: {structured_decisions}")

    return updated_state

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Initialize the graph
workflow = StateGraph(AgentState)

workflow.add_node("transcript_preprocessor", transcript_preprocessor_agent)
workflow.add_node("core_summarizer", core_summarizer_agent)
workflow.add_node("action_decision_extractor", action_decision_extractor_agent)
workflow.add_node("final_reporter", final_reporter_agent)

# --- MODIFIED SIMPLE_SUPERVISOR ---

def simple_supervisor(state: AgentState) -> Dict:
    print("\n--- Supervisor Check ---")
    print(f"  - Current cleaned_transcript: {'Set' if state.get('cleaned_transcript') else 'Not Set'}")
    print(f"  - Current meeting_summary: {'Set' if state.get('meeting_summary') else 'Not Set'}")
    print(f"  - Current action_items: {'Set' if state.get('action_items') else 'Not Set'}")
    print(f"  - Current final_report: {'Set' if state.get('final_report') else 'Not Set'}")

    next_node = None

    if not state.get("cleaned_transcript"):
        next_node = "transcript_preprocessor"
    elif not state.get("meeting_summary"): # Move to summarizer only after transcript is clean
        next_node = "core_summarizer"
    elif not state.get("action_items") or not state.get("key_decisions"): # Move to extractor only after summary (and transcript)
        next_node = "action_decision_extractor"
    elif not state.get("final_report"): # Move to reporter only after summary and extraction
        next_node = "final_reporter"
    else:
        next_node = END # End the graph

    print(f"Supervisor decided next node: {next_node}")
    return {"next_node": next_node}

workflow.add_node("supervisor", simple_supervisor)

# Set entry point
workflow.set_entry_point("supervisor")

# Define edges
# The supervisor decides the next step conditionally
workflow.add_conditional_edges(
    "supervisor",
    # This function determines the next node based on the state's 'next_node' field
    lambda state: state["next_node"],
    {
        "transcript_preprocessor": "transcript_preprocessor",
        "core_summarizer": "core_summarizer",
        "action_decision_extractor": "action_decision_extractor",
        "final_reporter": "final_reporter",
        END: END, # The supervisor can also decide to end the graph
    },
)

# After each agent (except final_reporter), return to the supervisor
workflow.add_edge("transcript_preprocessor", "supervisor")
workflow.add_edge("core_summarizer", "supervisor")
workflow.add_edge("action_decision_extractor", "supervisor")
workflow.add_edge("final_reporter", END) # The last node directly ends the graph

# Compile the graph
app = workflow.compile()

# This is the single function that Gradio will interact with.
def get_meeting_summary_report(transcript_text: str) -> str:
    """
    Invokes the LangGraph workflow with the given transcript and returns the final report.
    """
    # Basic validation for input
    if not transcript_text or transcript_text.strip() == "":
        return "Please provide a meeting transcript to summarize."

    # Initial state for the graph execution
    initial_state = {"raw_transcript": transcript_text, "next_node": "transcript_preprocessor"}

    try:
        # Invoke the compiled LangGraph application
        # This will run through all your agents based on supervisor's decisions
        final_state = app.invoke(initial_state)

        # Extract and return the final report
        if final_state.get("final_report"):
            return final_state["final_report"]
        else:
            # Fallback message if report is somehow not generated
            return "Summary generation completed, but the final report was not found in the state."
    except Exception as e:
        # Catch any errors during graph execution and return an informative message
        print(f"Error during graph execution: {e}")
        return f"An unexpected error occurred during summarization: {str(e)}"

# as `get_meeting_summary_report` will be imported and called by gradio_ui.py