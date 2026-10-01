# Import FastAPI so we can create our backend API
from fastapi import FastAPI

# Import StaticFiles so FastAPI can serve our frontend files
from fastapi.staticfiles import StaticFiles

# Import FileResponse so we can return the HTML page
from fastapi.responses import FileResponse

# Import BaseModel to define the structure of incoming Jira data
from pydantic import BaseModel

# Import the Groq client so our backend can communicate with Groq
from groq import Groq

# Import load_dotenv so we can read values from our .env file
from dotenv import load_dotenv

# Import os so we can access environment variables
import os


# Load the variables stored inside the .env file
load_dotenv()


# Get the Groq API key from the .env file
api_key = os.getenv("GROQ_API_KEY")


# Create the Groq client using the API key
client = Groq(api_key=api_key)


# Create the FastAPI application
app = FastAPI()

# Define the types of QA testing that the AI should consider
TEST_CATEGORIES = """
Generate test cases using these categories when they are relevant to the Jira requirement:

1. POSITIVE
- Verify valid inputs and expected successful behavior.
- Cover the normal user flow.

2. NEGATIVE
- Verify invalid, incorrect, missing, or unsupported inputs/actions.
- Verify appropriate validation or error handling when specified by the requirement.

3. EDGE
- Verify boundary values and unusual conditions.
- Consider minimum and maximum values.
- Consider empty values, very long values, special characters, and boundary
  conditions when applicable.

4. REGRESSION
- Verify related existing functionality that could be affected by the change.
- Verify that previously working behavior remains unchanged.
- Do not create unrelated regression tests.

5. BEHAVIORAL
- Verify relevant user interactions and state changes.
- Consider refreshing the page.
- Consider navigating away and returning.
- Consider browser Back and Forward navigation.
- Consider repeated actions or clicks.
- Consider canceling an action.
- Consider changing or clearing input.
- Only include behavioral tests when they are relevant to the affected feature.

IMPORTANT GENERATION RULES:
- Do not force every category into every ticket.
- Only generate categories that are relevant to the requirement.
- Prioritize coverage of the actual Jira requirement.
- Always generate test cases, even when the Jira ticket is short, general,
  or lacks detailed acceptance criteria.
- Never ask the user to provide more information before generating test cases.
- Use the Jira Summary and Description as the primary source of truth.
- When details are missing, create reasonable and observable tests based on
  the described feature or change.
- Do not invent specific application behavior, messages, buttons, pages,
  database values, API responses, usernames, or business rules.
- Do not assume authentication, submission, or other unrelated functionality.
- If expected behavior is unclear, generate the relevant test case and mark
  the uncertainty under a CLARIFICATIONS section.
- Clearly separate confirmed requirements from clarification items.
"""
OUTPUT_FORMAT = """
For every test case, use exactly this structure:

TEST_CASE_START

TEST_CASE_ID:
TC-001

CATEGORY:
Positive

SCENARIO:
Short description of what is being tested.

PRECONDITIONS:
Conditions required before testing.

TEST_DATA:
Specific test data, if applicable.

TEST_STEPS:
1. Step one
2. Step two
3. Step three

EXPECTED_RESULT:
Clear and observable expected behavior.

PRIORITY:
High

TEST_CASE_END

After all test cases, include:

CLARIFICATIONS:
- List any requirement that is unclear or needs confirmation
- If there is no clarifications, write a check symbol
"""

# Define the structure of the Jira ticket sent by the frontend
class JiraTicket(BaseModel):

    # Jira ticket ID
    ticket_id: str = ""

    # Jira ticket summary
    title: str = ""

    # Jira ticket description or acceptance criteria
    description: str = ""

    # Test coverage selected by the user
    coverage: str = "standard"

    # Test types selected by the user
    test_types: str = "all"


# Tell FastAPI where our frontend files are located
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# Handle requests to the main page
@app.get("/")
def home():

    # Return the frontend HTML file
    return FileResponse("frontend/index.html")


# Handle requests from the Generate Test Cases button
# Handle requests from the Generate Test Cases button
@app.post("/generate")
def generate_test_cases(ticket: JiraTicket):

    # Create the instructions that will be sent to the AI
    prompt = f"""
You are QAgent, an AI assistant for manual Software Quality Assurance.

Your task is to analyze the Jira ticket and generate useful manual QA
test cases.

The Jira ticket may be short, general, or incomplete. This is normal.
You must still generate test cases using the information available.

Do not ask the user for additional information.
Do not refuse to generate test cases.

{TEST_CATEGORIES}

{OUTPUT_FORMAT}

IMPORTANT:
- Follow the output format exactly.
- Do not use Markdown tables.
- Do not add introductions such as "I'm ready to generate test cases."
- Do not explain what you are about to do.
- Start directly with TEST_CASE_START.
- Generate only test cases relevant to the Jira ticket.

Jira Ticket ID:
{ticket.ticket_id}

Jira Summary:
{ticket.title}

Jira Description / Acceptance Criteria:
{ticket.description}

Test Coverage Requested:
{ticket.coverage}

Test Types Requested:
{ticket.test_types}
"""

    # Send the prompt to the Groq AI model
    response = client.chat.completions.create(

        # Use the Groq-supported model
        model="openai/gpt-oss-20b",

        # Send our QA instructions and Jira ticket to the AI
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        # Keep the output focused and reduce unnecessary creativity
        temperature=0.2
    )

    # Get the generated text from the AI response
    generated_result = response.choices[0].message.content

    # Send the generated test cases back to the frontend
    return {
        "result": generated_result
    }


    