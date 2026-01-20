import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict
import base64
import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def pdf_to_images(pdf_path: Path) -> List[bytes]:
    """
    Convert PDF pages to images (PNG format)

    Returns:
        List of image bytes for each page
    """
    images = []

    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]

        # Render page to image (300 DPI for good quality)
        pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))

        # Convert to PNG bytes
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)

    pdf_document.close()

    return images


def extract_transactions_from_image(image_bytes: bytes) -> List[Dict]:
    """
    Use OpenAI Vision API to extract transactions from bank statement image

    Returns:
        List of transaction dictionaries
    """

    # Encode image to base64
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Prompt for OpenAI Vision
    prompt = """
You are extracting transaction data from a bank statement image.

Extract ALL transactions from this bank statement page and return them as a JSON array.

For each transaction, extract:
- date: in YYYY-MM-DD format
- description: the merchant/payee name and details
- amount: the transaction amount as a number (use negative for debits/charges, positive for deposits/credits)
- type: either "Debit" or "Credit"

IMPORTANT:
- Debits (money out) should be NEGATIVE numbers
- Credits (money in) should be POSITIVE numbers
- If you see a "-" sign in the amount, make it negative
- Convert all dates to YYYY-MM-DD format
- Extract EVERY transaction on the page, don't skip any
- If there's a running balance column, ignore it

Return ONLY a valid JSON array like this:
[
  {
    "date": "2024-01-15",
    "description": "Amazon.com",
    "amount": -45.67,
    "type": "Debit"
  },
  {
    "date": "2024-01-16",
    "description": "Paycheck Deposit",
    "amount": 2500.00,
    "type": "Credit"
  }
]

If you cannot find any transactions, return an empty array: []
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Latest vision model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high",  # High detail for better accuracy
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
            temperature=0,  # Deterministic output
        )

        # Parse the JSON response
        content = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        transactions = json.loads(content)

        return transactions if isinstance(transactions, list) else []

    except Exception as e:
        print(f"Error extracting transactions from image: {e}")
        return []


def parse_pdf_statement(pdf_path: Path) -> List[Dict]:
    """
    Main function to parse PDF bank statement

    Process:
    1. Convert PDF pages to images
    2. Extract transactions from each page using AI
    3. Combine and deduplicate

    Returns:
        List of transaction dictionaries
    """

    all_transactions = []

    # Convert PDF to images
    images = pdf_to_images(pdf_path)

    print(f"Processing {len(images)} pages from PDF...")

    # Extract transactions from each page
    for page_num, image_bytes in enumerate(images, 1):
        print(f"Extracting transactions from page {page_num}...")

        try:
            page_transactions = extract_transactions_from_image(image_bytes)

            if page_transactions:
                print(
                    f"✓ Found {len(page_transactions)} transactions on page {page_num}"
                )
                # Log first transaction as example
                if len(page_transactions) > 0:
                    print(f"  Example: {page_transactions[0]}")
            else:
                print(f"✗ No transactions found on page {page_num}")

            all_transactions.extend(page_transactions)

        except Exception as e:
            print(f"✗ Error processing page {page_num}: {e}")
            continue

    # Sort by date
    all_transactions.sort(key=lambda x: x["date"])

    # Remove duplicates (sometimes transactions appear on multiple pages)
    seen = set()
    unique_transactions = []

    for trans in all_transactions:
        # Create unique key from date + description + amount
        key = f"{trans['date']}_{trans['description']}_{trans['amount']}"

        if key not in seen:
            seen.add(key)
            unique_transactions.append(trans)

    print(f"Total unique transactions: {len(unique_transactions)}")

    return unique_transactions
