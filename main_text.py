import os
import fitz
from PyPDF2 import PdfReader
from dotenv import load_dotenv

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        text_content = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text_content += page.extract_text()
    return text_content

def main():
    folder_path = os.getenv("DEFAULT_FILE_FOLDER")
    pdf_files = [file for file in os.listdir(folder_path) if file.endswith(".pdf")]
    for pdf_file in pdf_files:
        pdf_file_path = os.path.join(folder_path, pdf_file)
        folder_name = os.path.splitext(pdf_file)[0]
        pdf_folder_path = os.path.join(folder_path, folder_name)
        os.makedirs(pdf_folder_path, exist_ok=True)
        print(f"Created folder '{folder_name}'.")
        text_file_path = os.path.join(pdf_folder_path, folder_name+".txt")
        with open(text_file_path, "w") as text_file:
            text_file.write(extract_text_from_pdf(pdf_file_path))
        print(f"Created text file '{folder_name}.txt' in the folder.")
        pdf_file = fitz.open(pdf_file_path)

if __name__ == "__main__":
    load_dotenv()
    main()