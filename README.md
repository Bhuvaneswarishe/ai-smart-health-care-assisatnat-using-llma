Overview

The Healthcare Assistant is a prototype application designed to provide personalized health recommendations, including diet and workout plans, symptom analysis, and general health advice. It also allows users to upload health-related documents (e.g., medical reports), which the app analyzes to provide insights. The app leverages AI-based APIs for health-related Q&A and document analysis, aiming to assist users in better understanding their medical reports and overall health.
Features

    Personalized Recommendations: Provides tailored diet plans, workout routines, and general health advice based on user profile details (e.g., age, weight, height, medical conditions).
    Symptoms Checker: Offers users insights and suggestions based on the symptoms they provide.
    Document Analysis: Upload medical reports in PDF format to get simplified explanations and insights.
    Health Q&A: Uses Hugging Face models to answer health-related questions in real time.
    Future Enhancements:
        Health improvements visualization.
        Medical history storage for recurring users.
        Medical report explanation and personalized recommendations based on the reports.

Technology Stack

    Frontend: Streamlit
    APIs:
        SambaNova API for health-related query processing.
        
    Backend: Python
        function_calling.py and tools.py for handling API calls and managing user inputs.
        PyPDF2 for document parsing.
        Pandas for data handling.

