import os
import sys
import io

import streamlit as st
import yaml
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai
import PyPDF2

current_dir = os.path.dirname(os.path.abspath(__file__))
kit_dir = os.path.abspath(os.path.join(current_dir, '..'))
repo_dir = os.path.abspath(os.path.join(kit_dir, '..'))

sys.path.append(kit_dir)
sys.path.append(repo_dir)

from utils.model_wrappers.api_gateway import APIGateway

CONFIG_PATH = os.path.join(kit_dir, 'config.yaml')

# Load environment variables from .env file
load_dotenv(os.path.join(current_dir, '.env'))

def load_config():
    with open(CONFIG_PATH, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

config = load_config()

# Load API keys from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")

# Initialize Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_sambanova_response(query: str, context: str = "") -> str:
    try:
        llm = APIGateway.load_llm(
            type='sncloud',
            streaming=False,
            coe='FastCoE',
            do_sample=True,
            max_tokens_to_generate=1024,
            temperature=0.7,
            process_prompt=False,
            sambanova_api_key=SAMBANOVA_API_KEY,
        )
        
        prompt = f"""You are a helpful health care assistant. Provide a response based on the following query and context:

Query: {query}

Context: {context}

Please give a comprehensive and helpful response based on the information provided."""

        response = llm.invoke(prompt)
        return response
    except Exception:
        # Silently fall back to Gemini API without displaying an error message
        return get_gemini_response(prompt)

def get_gemini_response(prompt: str) -> str:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def personalized_recommendation_workspace():
    st.header("Personal Health Care Assistant")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120)
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0)
    with col2:
        height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0)
        medical_conditions = st.text_area("Medical Conditions (if any)")
    
    options = st.selectbox(
        "What kind of assistance do you need?",
        ("Diet Recommendations", "Workout Plans", "General Health Advice", "Symptom Checker", "Health Q&A")
    )

    if options in ["Diet Recommendations", "Workout Plans", "General Health Advice"]:
        if st.button("Get Personalized Advice", key="personalized_advice"):
            query = (f"User Details: Age - {age}, Weight - {weight}kg, Height - {height}cm, "
                     f"Medical Conditions - {medical_conditions}. ")
            
            if options == "Diet Recommendations":
                query += "Provide personalized diet recommendations."
            elif options == "Workout Plans":
                query += "Suggest an appropriate workout plan."
            else:
                query += "Provide general health advice and information."
            
            with st.spinner('Processing your request...'):
                response = get_sambanova_response(query)
            st.success("Here's your personalized advice:")
            st.write(response)

    elif options == "Symptom Checker":
        symptoms = st.text_area("Please describe your symptoms in detail:")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.text_input("How long have you been experiencing these symptoms?")
        with col2:
            severity = st.slider("On a scale of 1-10, how severe are your symptoms?", 1, 10)
        
        if st.button("Check Symptoms", key="check_symptoms"):
            query = f"Act as a medical professional. Symptom Check: Symptoms - {symptoms}, Duration - {duration}, Severity - {severity}/10. Provide a preliminary assessment and recommend next steps."
            
            with st.spinner('Analyzing your symptoms...'):
                response = get_sambanova_response(query)
            st.info("Symptom Analysis:")
            st.write(response)
            st.warning("Please note: This is not a substitute for professional medical advice. If you're concerned about your symptoms, please consult a healthcare provider.")

    else:  # Health Q&A
        user_query = st.text_input("Ask any health-related question:")
        
        if st.button("Get Answer", key="health_qa"):
            with st.spinner('Fetching your answer...'):
                prompt = f"Act as a knowledgeable healthcare professional. Answer the following health-related question: {user_query}"
                response = get_sambanova_response(prompt)
            st.success("Here's what I found:")
            st.write(response)
            st.info("This information is for educational purposes only. For medical advice, please consult a healthcare professional.")

def document_summary_workspace():
    st.header("Medical Document Summary and Analysis")
    
    uploaded_file = st.file_uploader("Upload your medical document", type=["txt", "pdf", "csv"])
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            file_contents = df.to_string()
        elif uploaded_file.type == "application/pdf":
            file_contents = extract_text_from_pdf(uploaded_file)
        else:
            file_contents = uploaded_file.getvalue().decode("utf-8")
        
        if st.button("Summarize and Analyze Document", key="analyze_document"):
            with st.spinner('Processing your document...'):
                # Use SambaNova to summarize the document
                summary_prompt = f"Summarize the following medical document in about 100 words:\n\n{file_contents}"
                doc_summary = get_sambanova_response(summary_prompt)
                st.subheader("Summary of Medical Document")
                st.info(doc_summary)
                
                # Use SambaNova to analyze the summary
                analysis_prompt = f"Analyze this medical document summary and provide key insights:\n\n{doc_summary}"
                analysis = get_sambanova_response(analysis_prompt)
                st.subheader("Analysis of Medical Document")
                st.success(analysis)

def main():
    st.set_page_config(
        page_title='AI-Powered Health Care Assistant',
        page_icon='🏥',
        layout="wide"
    )

    st.title('🏥 AI-Powered Health Care Assistant')

    workspace = st.sidebar.radio("Choose a workspace:", 
                         ("Personalized Recommendations", "Document Summary and Analysis"))
    
    if workspace == "Personalized Recommendations":
        personalized_recommendation_workspace()
    elif workspace == "Document Summary and Analysis":
        document_summary_workspace()

    # Footer
    st.sidebar.markdown("---")
    
if __name__ == '__main__':
    main()

#    streamlit run streamlit/app.py --browser.gatherUsageStats false
#    streamlit run streamlit/app.py --browser.gatherUsageStats false
