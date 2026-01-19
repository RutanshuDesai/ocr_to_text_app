import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from PIL import Image
import fitz
from dotenv import load_dotenv

from translation import SUPPORTED_EXTENSIONS, extract_text, extract_text_from_image, save_text


def ocr_pdf(pdf_path: str, language: str) -> str:
    text_chunks = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise ValueError("Unable to read PDF. Ensure it is a valid PDF file.") from exc

    with doc:
        for page in doc:
            pix = page.get_pixmap()
            mode = "RGBA" if pix.alpha else "RGB"
            page_image = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            if mode == "RGBA":
                page_image = page_image.convert("RGB")
            text_chunks.append(extract_text_from_image(page_image, language))

    return "\n\n".join(text_chunks).strip()


load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")

st.set_page_config(page_title="OCR to Text", page_icon="📄")
st.title("OCR to Text")
st.write("Upload a scanned PDF/TIF/image file and download the OCR text.")

if "is_authenticated" not in st.session_state:
    st.session_state.is_authenticated = False

if not APP_USERNAME or not APP_PASSWORD:
    st.error("App credentials not configured. Set APP_USERNAME and APP_PASSWORD.")
    st.stop()

with st.sidebar:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == APP_USERNAME and password == APP_PASSWORD:
            st.session_state.is_authenticated = True
        else:
            st.session_state.is_authenticated = False
            st.error("Invalid username or password.")

if not st.session_state.is_authenticated:
    st.info("Please log in to access the app.")
    st.stop()

uploaded_file = st.file_uploader(
    "Upload scanned file",
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
