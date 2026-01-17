import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from PIL import Image

from translation import SUPPORTED_EXTENSIONS, extract_text, save_text


def ocr_pdf(pdf_path: str, language: str) -> str:
    text_chunks = []
    with Image.open(pdf_path) as pdf:
        page_count = getattr(pdf, "n_frames", 1)
        for page_index in range(page_count):
            try:
                pdf.seek(page_index)
            except EOFError:
                break

            page = pdf.convert("RGB")
            with NamedTemporaryFile(delete=False, suffix=".png") as page_tmp:
                page_path = page_tmp.name

            try:
                page.save(page_path, format="PNG")
                text_chunks.append(extract_text(page_path, language))
            finally:
                try:
                    os.remove(page_path)
                except OSError:
                    pass

    return "\n\n".join(text_chunks).strip()


st.set_page_config(page_title="OCR to Text", page_icon="📄")
st.title("OCR to Text")
st.write("Upload a scanned PDF/TIF/image file and download the OCR text.")

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
                    text = ocr_pdf(input_path, language)
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
