import os
import re

from PyPDF2 import PdfReader
import fitz  

# Function to list all PDF files in nested directories
def list_pdf_files(folder_path):
    pdf_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

# Function to preprocess the text
def get_preprocessed_text(text):
    preprocessed_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower()).split()

    return preprocessed_text

# Function to retain original text
def get_original_text(text):
    original_text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\'\"-]', '', text).split()

    return original_text

def get_pdf_texts(base_folder_path):
    # Specify the base folder path containing nested folders with PDFs
    # base_folder_path = "./data"  # Replace with your actual path

    # List all PDF files in the specified folder and subfolders
    pdf_files = list_pdf_files(base_folder_path)
    print(f"[INFO] Found {len(pdf_files)} PDF files in nested folders.")

    # Dictionary to store PDF texts
    pdf_texts = {}

    # Process and extract text from each PDF file
    for pdf_file in pdf_files:
        try:
            # print(f"[INFO] Processing PDF: {pdf_file}")
            # reader = PdfReader(pdf_file)
            # text = ""
            # for page in reader.pages:
            #     text += page.extract_text()

            # # Store the extracted text
            # pdf_texts[os.path.basename(pdf_file)] = text
            # print(f"[SUCCESS] Processed {pdf_file}")
            print(f"[INFO] Processing PDF: {pdf_file}")
            # Open the PDF using PyMuPDF
            doc = fitz.open(pdf_file)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)  # Load each page
                text += page.get_text()  # Extract text from the page

            # Close the document after extraction
            doc.close()

            # Store the extracted text
            pdf_texts[os.path.basename(pdf_file)] = text
            print(f"[SUCCESS] Processed {pdf_file}")
        except Exception as e:
            print(f"[ERROR] Failed to process {pdf_file}: {e}")

    return pdf_texts