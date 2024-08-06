"""
Resume Experience App

Description: This app compares a job description to a resume and extracts
the number of years of relevant work experience from
the resume.
"""
import streamlit as st
from llm_agent.resume_analyzer import resume_analyzer_client
from streamlit_pdf_viewer import pdf_viewer
from datetime import datetime
import fitz

def display_chat_history(chat_container, messages):
    with chat_container:
        for _, message_ in enumerate(messages):
            with st.chat_message(message_["role"]):
                st.html(f"<span class='chat-{message_['role']}'></span>")
                st.write(message_["message"])

        st.html(
            """
            <style>
                .stChatMessage:has(.chat-user) {
                    flex-direction: row-reverse;
                    text-align: right;
                }
            </style>
            """
        )

def messages_to_string(messages):
    result = []
    for message in messages:
        role = message.get('role', 'unknown')
        content = message.get('message', '')
        result.append(f"{role}: {content}")
    return "\n".join(result)

def check_pdf_pages(file):
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    num_pages = pdf_document.page_count
    pdf_document.close()
    return num_pages

def extract_text_from_pdf(file):
    document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(document.page_count):
        page = document[page_num]
        text += page.get_text()
    return text

st.set_page_config(page_title="Resume Analyzer", layout="wide", page_icon='📚')

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("Resume Experience Analyzer 📝")
st.write("This app will compare a job description to a resume and extract the number of years of relevant work experience from the resume. Additionally, a chatbot is integrated to ask any questions related to the resume uploaded.")

resume_col, job_desc_col = st.columns([1, 0.9])

with resume_col:
    uploaded_file = st.file_uploader("Please upload your resume in PDF format here", type=["pdf"], key='pdf')
    if uploaded_file:
        uploaded_file.seek(0)  # Reset file pointer for page checking
        num_pages = check_pdf_pages(uploaded_file)
        if num_pages > 3:
            st.error(f"Error: The resume PDF exceeds the maximum allowable pages (3). It has {num_pages} pages. Please upload a shorter resume.")
            st.session_state.resume_content = None
            st.session_state.pdf_ref = None
        else:
            uploaded_file.seek(0)  # Reset file pointer for text extraction
            resume_content = extract_text_from_pdf(uploaded_file)
            st.session_state['resume_content'] = resume_content
            st.session_state.pdf_ref = uploaded_file
    else:
        st.session_state.resume_content = None
        st.session_state.pdf_ref = None


with job_desc_col:
    today_date = datetime.today().strftime('%Y-%m-%d')

    job_description_option = st.radio("Would you like to input the job description as text or PDF?", ("Text", "PDF"), index=None)
    if job_description_option == "Text":
        st.session_state.job_description_option = 'Text'
        job_description_text = st.text_area("Please enter the job description here")
        if job_description_text:
            st.session_state.job_description = job_description_text
            if 'resume_content' in st.session_state:
                st.session_state.experience = resume_analyzer_client.retrieve_experience(pdf_content=st.session_state.resume_content, job_description=job_description_text, date=today_date)
        else:
            if 'job_description' in st.session_state:
                del st.session_state.job_description
            if 'experience' in st.session_state:
                del st.session_state.experience
    elif job_description_option == "PDF":
        st.session_state.job_description_option = 'PDF'
        job_description_file = st.file_uploader("Please upload the job description in PDF format here", type=["pdf"], key='job_desc_pdf')
        if job_description_file:
            job_description_content = extract_text_from_pdf(job_description_file)
            st.session_state.job_description = job_description_content
            st.session_state.job_desc_ref = job_description_file
            if 'resume_content' in st.session_state:
                st.session_state.experience = resume_analyzer_client.retrieve_experience(pdf_content=st.session_state.resume_content, job_description=job_description_content, date=today_date)
        else:
            st.session_state.job_desc_ref = None
            if 'job_description' in st.session_state:
                del st.session_state.job_description
            if 'experience' in st.session_state:
                del st.session_state.experience

if 'experience' in st.session_state and st.session_state.experience :
    with st.expander("Candidate's Prior Experience Details", expanded=True):
        st.markdown(f'###### Total Work Experience : `{st.session_state.experience[0]}`', unsafe_allow_html=True)
        st.markdown(f'###### Total Work Experience relevant to the Job Description : `{st.session_state.experience[1]}`', unsafe_allow_html=True)

input_and_chat, pdf_preview = st.columns([1,0.9])
with input_and_chat:
    if 'resume_content' in st.session_state and st.session_state.resume_content:
        with st.expander('Chat with your Resume', expanded=True):
            chat_container = st.container()
            display_chat_history(chat_container, st.session_state.messages)
            if uploaded_file is not None:
                prompt = st.chat_input('Ask anything about your PDF')
                if prompt:
                    with st.spinner("Generating Response"):
                        job_description = 'Not uploaded yet'
                        if 'job_description' in st.session_state and st.session_state.job_description:
                            job_description = st.session_state.job_description
                        results = resume_analyzer_client.answer_question(st.session_state.resume_content, prompt, messages_to_string(st.session_state.messages), job_description)
                        st.session_state.messages += [{'role': 'user', 'message': prompt}]
                        st.session_state.messages += [{'role': 'assistant', 'message': results}]
                        display_chat_history(chat_container, st.session_state.messages[-2:])

if 'pdf_ref' in st.session_state and 'job_desc_ref' in st.session_state and st.session_state.pdf_ref and st.session_state.job_desc_ref:
    with pdf_preview:
        with st.expander('Resume PDF Preview', expanded=True):
            binary_data = st.session_state.pdf_ref.getvalue()
            pdf_viewer(input=binary_data)

    with pdf_preview:
        with st.expander('Job Description PDF Preview', expanded=True):
            binary_data_job = st.session_state.job_desc_ref.getvalue()
            pdf_viewer(input=binary_data_job)

elif 'pdf_ref' in st.session_state and st.session_state.pdf_ref:
    with pdf_preview:
        with st.expander('Resume PDF Preview', expanded=True):
            binary_data = st.session_state.pdf_ref.getvalue()
            pdf_viewer(input=binary_data)
