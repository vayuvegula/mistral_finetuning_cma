"""
Script to extract EPUB content to a text file.
Libraries required:
pip install ebooklib beautifulsoup4

This script reads an EPUB file, extracts the textual content while cleaning up excessive whitespace,
and saves the cleaned text into an output file. The output text file is formatted with paragraphs
separated by double newlines for readability.

Usage:
- Ensure you have the necessary libraries installed.
- Update the `epub_path` variable with the path to your EPUB file.
- Run the script to generate the `output.txt` file.

"""

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def epub_to_text(epub_path):
    """
    Extract text from an EPUB file and clean up excessive whitespace.

    Args:
    epub_path (str): The file path to the EPUB file.

    Returns:
    str: The cleaned textual content of the EPUB file.
    """
    book = epub.read_epub(epub_path)
    text = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse the content of the document item as HTML
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            # Extract text, replace multiple whitespaces with a single space, and strip leading/trailing whitespace
            page_text = soup.get_text(separator=" ").strip()
            page_text = ' '.join(page_text.split())
            # Ensure paragraphs are separated by double newlines
            text += page_text + "\n\n"
    return text

# Update the path to your EPUB file here
epub_path = "PoorCharliesAlmanack.epub"
# Extract text from the EPUB file and clean it up
text = epub_to_text(epub_path)
# Save the cleaned text to an output file
with open("output.txt", "w") as f:
    f.write(text)

print("Text extraction complete. Saved to output.txt.")