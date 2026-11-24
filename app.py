import os

import requests
import streamlit as st

st.set_page_config(page_title="Hello Agent", page_icon="💬", layout="centered")
st.title("Hello Agent")
st.caption("Ask questions about your CSV files and get answers grounded in their data.")

with st.sidebar:
    st.header("Your data")
    include_samples = st.checkbox("Include the example datasets", value=True)
    uploads = st.file_uploader(
        "Upload CSV files",
        type=["csv"],
        accept_multiple_files=True,
        help="Upload one or more CSV files (up to 10 files; 5 MB each).",
    )
    st.caption("Answers are based only on matching rows in the selected files.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

has_data = include_samples or bool(uploads)
if not has_data:
    st.info("Enable the example datasets or upload at least one CSV to get started.")

question = st.chat_input("Ask a question about your CSV data", disabled=not has_data)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    form_data = {
        "question": question,
        "include_samples": str(include_samples).lower(),
    }
    multipart_files = [
        ("files", (upload.name, upload.getvalue(), "text/csv"))
        for upload in (uploads or [])
    ]

    with st.chat_message("assistant"):
        with st.spinner("Searching your CSV data..."):
            try:
                response = requests.post(
                    f"{os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/')}/api/ask",
                    data=form_data,
                    files=multipart_files or None,
                    timeout=(5, 120),
                )
            except requests.RequestException as error:
                st.error(f"Could not reach the Hello Agent backend: {error}")
            else:
                if not response.ok:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Backend error ({response.status_code}): {detail}")
                else:
                    try:
                        answer = response.json()["answer"]
                    except (ValueError, KeyError, TypeError) as error:
                        st.error(f"The backend returned an invalid response: {error}")
                    else:
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
