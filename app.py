import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from dotenv import load_dotenv

from translation import SUPPORTED_EXTENSIONS, extract_text, ocr_pdf, save_text


load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

st.set_page_config(page_title="Shivam Services OCR", page_icon="🚀")
st.title("Regional Language Text Extractor")
st.write("Upload a scanned TIF/image file or a PDF and download the OCR text.")



if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if not APP_USERNAME or not APP_PASSWORD:
    st.error("App credentials not configured. Set APP_USERNAME and APP_PASSWORD.")
    st.stop()

with st.sidebar:
    st.markdown('<div style="color: #888; font-size: 1.4em; text-align: left; margin-bottom: 0.5em;">Shivam Services</div>', unsafe_allow_html=True)
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.is_authenticated = True
        else:
            st.session_state.is_authenticated = False
            st.error("Invalid username or password.")

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #888; font-size: 0.9em; text-align: left; margin-bottom: 1.9em;"><i>Made by Rutanshu Desai</i></div>', unsafe_allow_html=True)

if not st.session_state.is_authenticated:
    st.info("Please log in to access the app.")
    st.stop()

uploaded_file = st.file_uploader(
    "",
    type=["pdf", "tif", "tiff", "png", "jpg", "jpeg"],
)
language = st.text_input("Tesseract language code", value="guj")

if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = None
if "download_name" not in st.session_state:
    st.session_state.download_name = None
if "last_upload" not in st.session_state:
    st.session_state.last_upload = None

if uploaded_file:
    if st.session_state.last_upload != uploaded_file.name:
        st.session_state.last_upload = uploaded_file.name
        st.session_state.ocr_text = None
        st.session_state.download_name = None

    run_ocr = st.button("Run OCR")
    if run_ocr:
        with st.spinner("Running OCR..."):
            suffix = Path(uploaded_file.name).suffix.lower()
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp_input:
                tmp_input.write(uploaded_file.getbuffer())
                input_path = tmp_input.name

            try:
                if suffix == ".pdf":
                    try:
                        text = ocr_pdf(input_path, language)
                    except ValueError as exc:
                        st.error(str(exc))
                        text = ""
                elif suffix in SUPPORTED_EXTENSIONS:
                    text = extract_text(input_path, language)
                else:
                    st.error("Unsupported file type.")
                    text = ""

                if text.strip():
                    with NamedTemporaryFile(delete=False, suffix=".txt") as tmp_output:
                        output_path = tmp_output.name
                    save_text(text, output_path)
                    st.session_state.ocr_text = text
                    st.session_state.download_name = f"{Path(uploaded_file.name).stem}.txt"

                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                else:
                    st.warning("No text extracted from the file.")
            finally:
                try:
                    os.remove(input_path)
                except OSError:
                    pass

if st.session_state.ocr_text:
    st.success("OCR complete.")
    st.download_button(
        "Download text file",
        data=st.session_state.ocr_text,
        file_name=st.session_state.download_name or "output.txt",
        mime="text/plain",
    )