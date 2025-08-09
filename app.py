# Streamlit/Flask UI for uploading & ranking
import streamlit as st
import json
from pathlib import Path

def main():
    st.title("Resume Matcher")
    st.write("Upload resumes and job descriptions to find the best matches")
    
    # File upload section
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt', 'docx'])
    
    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        # TODO: Add processing logic
    
    # Job description input
    job_description = st.text_area("Enter job description:")
    
    if st.button("Find Matches"):
        if job_description:
            st.write("Processing matches...")
            # TODO: Add matching logic
        else:
            st.warning("Please enter a job description")

if __name__ == "__main__":
    main()