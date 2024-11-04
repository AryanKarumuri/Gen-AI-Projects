# Text Processing 📄 and PDF Generation 🖨️ using Mistral-7B-Instruct Model 🤖

## Overview🌟
This Python script utilizes the Intel Extension for PyTorch and the Hugging Face Transformers library to process input text and convert it into a structured tabular format and release notes. It also generates PDF documents from the outputs. The script employs the Mistral-7B-Instruct model for text generation.

## Requirements📋
- Python: Version 3.7 or higher
- reportlab: For generating PDF documents
- tabulate: For formatting output in tables
- pypdf: For merging PDF files
- Hugging Face Transformers: For accessing pre-trained models
- PyTorch with Intel Extension: For optimized model performance on Intel hardware

## Verified Environment✅

- Platform: [Intel® Tiber™ Developer Cloud](https://www.intel.com/content/www/us/en/developer/tools/devcloud/services.html)

- Hardware: [Intel® Data Center GPU Max Series](https://www.intel.com/content/www/us/en/products/details/discrete-gpus/data-center-gpu/max-series.html)

## Model Details
The script uses the model `mistralai/Mistral-7B-Instruct-v0.1`. Ensure you have access to this model through the Hugging Face Hub.

## Usage 📚

### Convert a Paragraph to Tabular Format

- The script prompts the user to input a paragraph.
- It generates a nested Python list containing component names and versions.
- The result is printed in a tabular format.

### Generate Release Notes

- The user is prompted to enter another paragraph.
- The script converts this paragraph into concise bullet points formatted as release notes.
- These notes are printed to the console.

### PDF Generation

- The script generates two PDFs:
  - output1.pdf: Contains the table of components and versions.
  - table.pdf: Contains the formatted release notes.
- Finally, both PDFs are merged into a single file named **result.pdf**.

