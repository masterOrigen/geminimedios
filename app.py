import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="PDF Q&A with Gemini",
    page_icon="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png",
    layout="wide",
)

st.markdown('''
# PDF Q&A with Gemini AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="30" height="30">
''', unsafe_allow_html=True)

#------------------------------------------------------------
#LANGUAGE
#LANGUAGE
# Columna de idioma
lang = 'Español'
st.divider()

#------------------------------------------------------------
#FUNCTIONS
def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.
    """
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def append_message(message: dict) -> None:
    """
    Append a message to the chat session.
    """
    st.session_state.chat_session.append({'user': message})

@st.cache_resource
def load_model() -> genai.GenerativeModel:
    """
    Load the Gemini model for text processing.
    """
    model = genai.GenerativeModel('gemini-pro')
    return model



#------------------------------------------------------------
#CONFIGURATION
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = load_model()

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = []

if 'pdf_content' not in st.session_state:
    st.session_state.pdf_content = None

#------------------------------------------------------------
#PDF UPLOAD
if lang == 'Español':
    pdf_file = st.file_uploader("Sube tu archivo PDF", type=['pdf'])
    placeholder_text = "Escribe tu pregunta sobre el PDF..."
    processing_text = "Procesando el PDF..."
    no_pdf_text = "Por favor, sube un archivo PDF primero."
else:
    pdf_file = st.file_uploader("Upload your PDF file", type=['pdf'])
    placeholder_text = "Ask a question about the PDF..."
    processing_text = "Processing the PDF..."
    no_pdf_text = "Please upload a PDF file first."

if pdf_file is not None:
    if 'current_pdf' not in st.session_state or st.session_state.current_pdf != pdf_file.name:
        with st.spinner(processing_text):
            st.session_state.pdf_content = extract_text_from_pdf(pdf_file)
            st.session_state.current_pdf = pdf_file.name
            st.session_state.chat_session = []

#------------------------------------------------------------
#CHAT INTERFACE
if len(st.session_state.chat_session) > 0:
    for message in st.session_state.chat_session:
        if message['user']['role'] == 'model':
            with st.chat_message('ai'):
                st.write(message['user']['parts'])
        else:
            with st.chat_message('user'):
                st.write(message['user']['parts'][0])

if st.session_state.pdf_content is None:
    st.warning(no_pdf_text)
else:
    prompt = st.chat_input(placeholder_text)
    
    if prompt:
        prmt = {'role': 'user', 'parts': [prompt]}
        append_message(prmt)
        
        with st.spinner(processing_text):
            context = f"Context from PDF:\n{st.session_state.pdf_content}\n\nQuestion: {prompt}"
            response = model.generate_content(context)
            
            try:
                append_message({'role': 'model', 'parts': response.text})
                st.rerun()
            except Exception as e:
                append_message({'role': 'model', 'parts': f'{type(e).__name__}: {e}'})
                st.rerun()
