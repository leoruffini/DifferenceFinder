# main.py

import os
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from docx import Document
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="DOCX Difference Highlighter")

class DocumentProcessor:
    """
    Handles the processing of DOCX files.
    """

    def __init__(self, file: UploadFile):
        self.file = file
        self.text = ""

    def save_to_temp(self) -> str:
        """
        Saves the uploaded file to a temporary location.
        Returns the path to the temporary file.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                shutil.copyfileobj(self.file.file, tmp)
                temp_path = tmp.name
            return temp_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    def extract_text(self, file_path: str) -> str:
        """
        Extracts text from a DOCX file.
        """
        try:
            doc = Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    def process(self) -> str:
        """
        Processes the uploaded file and extracts text.
        """
        temp_path = self.save_to_temp()
        text = self.extract_text(temp_path)
        os.unlink(temp_path)  # Clean up the temporary file
        return text

class GPTDifferenceFinder:
    """
    Uses GPT-4 to find differences between two texts using the new OpenAI API for version >=1.0.0.
    """

    def __init__(self, text1: str, text2: str):
        self.text1 = text1
        self.text2 = text2
        self.differences = ""

    def find_differences(self):
        """
        Sends a prompt to GPT-4 using the updated chat endpoint to find differences between two texts.
        """
        prompt = (
            "Compare the following two documents and list all the differences between them. "
            "Provide the differences in a clear and concise manner.\n\n"
            "Document 1:\n"
            f"{self.text1}\n\n"
            "Document 2:\n"
            f"{self.text2}\n\n"
            "Differences:"
        )

        try:
            # Using the new `openai.Chat.create()` method in the latest API
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI that compares two documents and highlights their differences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2,
            )

            # Correct way to access the message content
            self.differences = response.choices[0].message.content.strip()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error communicating with GPT-4: {e}")

    def get_differences(self) -> str:
        """
        Returns the differences after processing.
        """
        if not self.differences:
            self.find_differences()
        return self.differences
    

# main.py

from fastapi.middleware.cors import CORSMiddleware

# Define allowed origins
origins = [
    "http://localhost",  # If you open the HTML file locally
    "http://localhost:8000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development purposes. In production, specify allowed origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compare-docx/", summary="Compare two DOCX files and return differences.")
async def compare_docx(file1: UploadFile = File(..., description="First DOCX file"), 
                      file2: UploadFile = File(..., description="Second DOCX file")):
    """
    Endpoint to compare two DOCX files and return the differences as a JSON response.
    """

    # Validate file types
    if file1.content_type != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        raise HTTPException(status_code=400, detail="file1 must be a .docx file.")
    if file2.content_type != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        raise HTTPException(status_code=400, detail="file2 must be a .docx file.")

    # Process both documents
    processor1 = DocumentProcessor(file1)
    text1 = processor1.process()

    processor2 = DocumentProcessor(file2)
    text2 = processor2.process()

    # Find differences using GPT-4
    difference_finder = GPTDifferenceFinder(text1, text2)
    differences = difference_finder.get_differences()

    # Return the differences as a JSON response
    return JSONResponse(content={"differences": differences})