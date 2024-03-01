import PyPDF2

def read_attach_pdf(file_name):
    with open(file_name, "rb") as f:
        pdfReader = PyPDF2.PdfReader(f)
        content = ""
        for page in pdfReader.pages:
            content += page.extract_text()
        return content