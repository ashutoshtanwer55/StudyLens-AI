import streamlit as st
import os
import requests
import fitz  # PyMuPDF
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Study Assistant Agent", page_icon="📚", layout="wide")

st.title("📚 AI Study & Content Assistant Agent")
st.markdown("PDF ya koi bhi Web Link upload/paste karo aur **Summary, Important Questions, aur MCQs** ek click mein pao!")

# --- SIDEBAR: API KEY & INPUTS ---
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

st.sidebar.header("📥 Choose Source")
input_type = st.sidebar.selectbox("Select Input Type", ["PDF Document", "Web Link (LinkedIn/Blog)"])

source_text = ""

if input_type == "PDF Document":
    uploaded_file = st.sidebar.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            doc = fitz.open("temp.pdf")
            for page in doc:
                source_text += page.get_text() + "\n"
            st.sidebar.success("✅ PDF Loaded Successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading PDF: {e}")

elif input_type == "Web Link (LinkedIn/Blog)":
    web_url = st.sidebar.text_input("Enter Web / LinkedIn Link")
    if web_url:
        try:
            jina_url = f"https://r.jina.ai/{web_url}"
            response = requests.get(jina_url)
            if response.status_code == 200:
                source_text = response.text
                st.sidebar.success("✅ Web Link Loaded via Jina Reader!")
            else:
                st.sidebar.error(f"Failed to fetch. Status: {response.status_code}")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# --- MAIN GENERATION LOGIC ---
if st.button("🚀 Generate Study Material"):
    if not api_key:
        st.error("⚠️ Pehle sidebar mein apni Google Gemini API Key enter karo!")
    elif not source_text.strip():
        st.warning("⚠️ Pehle koi valid PDF ya Web link do!")
    else:
        with st.spinner("🤖 AI is analyzing the content and generating material..."):
            try:
                # Locked explicitly to gemini-3.8-flash as requested
                model = genai.GenerativeModel('gemini-3.8-flash')
                
                prompt = f"""
                You are an expert academic tutor and study assistant. Analyze the following text carefully and generate:
                1. **Key Summary & Important Points** (Bullet points of core concepts).
                2. **Important Subjective Questions & Answers** (Exam-style questions with clear answers).
                3. **Multiple Choice Questions (MCQs)** (5 MCQs with options, correct answers, and short explanations).

                Here is the content:
                {source_text[:30000]}
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred with Gemini API: {e}")