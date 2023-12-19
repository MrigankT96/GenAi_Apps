import fitz  # PyMuPDF
import os
import tempfile
import base64
import requests
import pandas as pd
from io import StringIO
import logging
from datetime import datetime

# Configure logging to append to a log file and include the date and time
logging.basicConfig(filename='visionPdf/process_logs.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

# Function to calculate the estimated cost of API usage
def calculate_price(tokens_used, price_per_1k_tokens=0.01):
    """Calculate the estimated cost of API usage based on tokens used."""
    return (tokens_used / 1000) * price_per_1k_tokens

# Function to convert PDF pages to images
def pdf_to_images(pdf_path, zoom_factor=2.0):
    """Convert each page of a PDF to an image and return the list of image paths."""
    images = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=mat)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            pix.save(temp_file.name)
            images.append((temp_file.name, pix.width, pix.height))
    doc.close()
    return images

# Function to encode an image in base64
def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to call OpenAI API with the encoded image
def call_openai_api(api_key, image_path):
    """Make a request to the OpenAI API with the given image."""
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {"type": "text", "text": "Extract information from the tables in the image and return structured table output as a csv. Consider that there can be hierarchical relationships in the tables. Please return only the output, and no other sentences. Don't include '```csv' in the output's beginning."},
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 2000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response

# Function to create a pandas DataFrame from the API response
def create_dataframe_from_response(response):
    """Convert API response to pandas DataFrame."""
    try:
        data = response.json()['choices'][0]['message']['content']
        # Attempt to read the CSV data
        data_io = StringIO(data)
        df = pd.read_csv(data_io)
    except pd.errors.ParserError as e:
        # Log the parser error
        logging.error(f"Failed to parse CSV data: {e}")
        # Attempt to recover by splitting the data manually, or return an empty DataFrame
        df = pd.DataFrame()
    return df


# Main processing function
def process_pdf_to_csv(api_key, pdf_path, csv_output_path, zoom_factor=4.0):
    """Process each page of a PDF, extract data using OpenAI API, and save as CSV."""
    total_cost = 0
    total_tokens = 0
    images = pdf_to_images(pdf_path, zoom_factor)
    pdf_base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for i, (image_path, width, height) in enumerate(images):
        response = call_openai_api(api_key, image_path)
        df = create_dataframe_from_response(response)
        csv_file_name = f"vision_extracted_{pdf_base_name}_page_{i+1}.csv"
        df.to_csv(os.path.join(csv_output_path, csv_file_name), index=False)
        
        tokens_used = response.json().get('usage', {}).get('total_tokens', 0)
        cost = calculate_price(tokens_used)
        total_cost += cost
        total_tokens += tokens_used
        logging.info(f"CSV file {csv_file_name} created for page {i+1}, Image resolution: {width}x{height}, Tokens used: {tokens_used}, Cost: ${cost:.5f}")
        
        os.remove(image_path)  # Clean up the temporary image file
    
    # Log total cost and tokens for the PDF
    logging.info(f"Pdf processed. Used Model: gpt-4-vision-preview, Total Tokens used: {total_tokens}, Total Estimated cost for \"{pdf_base_name}\": ${total_cost:.5f}")

# Implementation

    
api_key = input("Enter your OpenAI API key: ")
input_pdf_directory = input("Enter the input PDF file path: ")
output_csv_directory = input("Enter the output CSV directory path: ")

process_pdf_to_csv(api_key, input_pdf_directory, output_csv_directory, zoom_factor=4.0)
