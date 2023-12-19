# PDF to CSV Data Extractor


# Introduction
The PDF to CSV Data Extractor is a Python application designed to process PDF files, extract data from them using OpenAI's GPT-4 Vision API, and save the extracted data as CSV files. This tool is particularly useful for converting tabular data in PDFs into a more accessible and manipulable CSV format.

# Features
Converts PDF pages to images.
Uses OpenAI's GPT-4 Vision API to extract tabular data from images.
Saves extracted data in CSV format.
Estimates the cost of API usage.
Logs processing details for monitoring and debugging.
# Requirements
Python 3.x
Libraries: PyMuPDF (fitz), pandas, requests
An OpenAI API key


# Installation
Clone the repository or download the script.
Install required Python libraries:

pip install fitz pandas requests

Ensure you have an OpenAI API key.
# Usage
Run the script from the command line:

python process_pdf_to_csv.py

When prompted, enter your OpenAI API key, the input PDF file path, and the output CSV directory path.


# Configuration
The script uses interactive input for the OpenAI API key and file paths.
Logging configurations can be modified in the script.

# Output:
The script generates CSV files corresponding to each page of the input PDF.
Logs are saved in 'visionPdf/process_logs.log'.

# Contributing
Contributions to enhance the functionality of this script are welcome. Please feel free to fork the repository and submit pull requests.

# License
unlicensed

# Contact
For any queries or suggestions, please contact mriganktiwari96@gmail.com

