from docx import Document

def extract_text_from_docx(uploaded_file):
    document = Document(uploaded_file.file)
    text = "\n".join([para.text for para in document.paragraphs])
    return text
