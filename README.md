To run the project: 

1.- Install the dependencies and run the following command:
pip install -r requirements.txt

2.- Ensure that your .env file is properly set up with the necessary environment variables, especially the OPENAI_API_KEY.
.env
OPENAI_API_KEY=your_openai_api_key_here.

3.- Run the Application
Use Uvicorn to run your FastAPI application. Uvicorn is an ASGI server implementation, used to serve FastAPI applications.

uvicorn main:app --reload

5. Access the Application
Open index.html located in the docx-diff-frontend directory.

6. Upload DOCX Files
Use the file upload feature to compare two DOCX files.

7. View Differences
The application will display the differences between the two DOCX files in a new DOCX file.