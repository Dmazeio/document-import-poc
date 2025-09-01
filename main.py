# main.py

import os
import json
import pdfplumber  # Import the new library
from openai import OpenAI
from dotenv import load_dotenv

# --- CONFIGURATION ---
# 1. Load environment variables from the .env file
load_dotenv()

# 2. Get the API key and initialize the OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Could not find OPENAI_API_KEY. Check your .env file.")
client = OpenAI(api_key=api_key)


# --- FUNCTIONS ---

def extract_text_from_pdf(file_path):
    """
    Opens a PDF file and extracts all text from all pages.
    Returns the text as a single string.
    """
    print(f"Reading text from PDF file: {file_path}...")
    try:
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n" # Add a newline between pages
        return full_text
    except FileNotFoundError:
        return {"error": f"The file was not found at the path: {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while reading the PDF: {e}"}

def extract_meeting_data_as_json(meeting_text):
    """
    Sends unstructured meeting text to OpenAI and requests structured JSON in return.
    """
    # Define the template for the data we want in return
    data_template = """
    {
        "title": "...",
        "description": "...",
        "date": "YYYY-MM-DD"
    }
    """
    
    # Define a detailed instruction for the model
    system_instruction = f"""
    You are an expert at analyzing minutes of meetings.
    Analyze the user's text. Extract the following data fields:
    1.  'title': The main title of the meeting.
    2.  'description': A brief summary of the meeting's purpose.
    3.  'date': The date of the meeting.
    
    Format your response as a valid JSON object based on this template:
    {data_template}
    
    Respond ONLY with the JSON object itself.
    """

    try:
        print("Sending text to OpenAI for analysis...")
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": meeting_text}
            ]
        )
        json_response_str = response.choices[0].message.content
        return json.loads(json_response_str)

    except json.JSONDecodeError:
        return {"error": "Failed to decode the JSON response from OpenAI."}
    except Exception as e:
        return {"error": f"An error occurred during the call to OpenAI: {e}"}


# --- MAIN LOGIC ---
if __name__ == "__main__":
    # Define the path to the PDF file you want to analyze
    pdf_file_path = "Minutes_of_meeting_samples/SampleMinutes-1.pdf"
    
    # Step 1: Extract text from the PDF
    raw_text_from_pdf = extract_text_from_pdf(pdf_file_path)
    
    # Check if text extraction was successful
    if isinstance(raw_text_from_pdf, dict) and "error" in raw_text_from_pdf:
        print(f"Error: {raw_text_from_pdf['error']}")
    else:
        print("Text successfully extracted from PDF.")
        
        # Step 2: Send the text to OpenAI to get structured data
        structured_data = extract_meeting_data_as_json(raw_text_from_pdf)
        
        print("\n--- Result from OpenAI ---")
        # Use json.dumps to "pretty-print" the result with indentation
        print(json.dumps(structured_data, indent=2, ensure_ascii=False))
        print("--------------------------")