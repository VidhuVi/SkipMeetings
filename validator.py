# validator.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

class TranscriptValidator:
    def __init__(self):
        # Using a low temperature for deterministic classification
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert text classifier. Your task is to determine if the given text is a meeting transcript, meeting notes, an agenda, or any other content directly related to a business or academic meeting. Respond with ONLY 'YES' if it is, and 'NO' if it is not. Provide no other text or explanation."),

            # --- FEW-SHOT EXAMPLES START ---
            # Good Example 1 (Transcript Snippet)
            HumanMessage(content="Text: John: Let's discuss Q3 budget. Sarah: I'll send the report. David: Action item: Sarah to send report by Friday. Is this meeting-related content? (YES/NO)"),
            AIMessage(content="YES"),

            # Bad Example 1 (Random Text)
            HumanMessage(content="Text: The quick brown fox jumps over the lazy dog. Is this meeting-related content? (YES/NO)"),
            AIMessage(content="NO"),

            # Good Example 2 (Meeting Agenda)
            HumanMessage(content="Text: Meeting Agenda:\n1. Welcome\n2. Review past action items\n3. New business\n4. AOB\n5. Close. Is this meeting-related content? (YES/NO)"),
            AIMessage(content="YES"),

            # Bad Example 2 (Personal Message)
            HumanMessage(content="Text: Hey, just checking in. Are we still on for dinner tonight? Is this meeting-related content? (YES/NO)"),
            AIMessage(content="NO"),

            # Good Example 3 (Very Short Meeting Note)
            HumanMessage(content="Text: Minutes: Project Alpha Status - Green. Next Steps: Report due 10/10. Is this meeting-related content? (YES/NO)"),
            AIMessage(content="YES"),
            # --- FEW-SHOT EXAMPLES END ---

            ("human", "Text: {text}\nIs this meeting-related content? (YES/NO)")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def validate(self, text: str) -> bool:
        # ... (rest of your validate method remains the same) ...
        if not text or len(text.strip()) < 50:
            print("Validation: Text too short or empty.")
            return False

        try:
            response = self.chain.invoke({"text": text.strip()})
            cleaned_response = response.strip().upper()

            if cleaned_response == "YES":
                print("Validation: PASSED (Meeting-related content detected).")
                return True
            elif cleaned_response == "NO":
                print("Validation: FAILED (Not meeting-related content).")
                return False
            else:
                print(f"Validation: Unexpected LLM response '{cleaned_response}'. Assuming FAILED.")
                return False
        except Exception as e:
            print(f"Error during validation LLM call: {e}. Assuming FAILED.")
            return False

if __name__ == "__main__":
    validator = TranscriptValidator()
    print(f"Test 1 (Good transcript): {validator.validate('John: Let us discuss the next steps. Sarah: I will send out the notes.')}")
    print(f"Test 2 (Random text): {validator.validate('This is just some random text about a cat and a dog.')}")
    print(f"Test 3 (Meeting agenda): {validator.validate('Agenda for today: 1. Old Business. 2. New Proposals. 3. Action Items.')}")
    print(f"Test 4 (Short non-meeting): {validator.validate('Hello there.')}")
    print(f"Test 5 (Short meeting note): {validator.validate('Decisions: Finalize report by EOD. Assigned to: Team A.')}")