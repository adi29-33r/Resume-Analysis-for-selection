import pdfplumber
import tempfile

async def extract_text_from_pdf(uploaded_file):
    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        content = await uploaded_file.read()
        temp.write(content)
        temp.flush()
        temp_path = temp.name

    text = ""
    with pdfplumber.open(temp_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text
