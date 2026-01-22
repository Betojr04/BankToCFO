from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from pathlib import Path
import uuid
from datetime import datetime

from services.parser import parse_bank_statement
from services.categorizer import categorize_transactions
from services.excel_generator import generate_cfo_pack
from dotenv import load_dotenv

load_dotenv()  # Add this line at the very top, before anything else

app = FastAPI(title="BankToCFO API", version="1.0.0")

# CORS setup - allow Lovable frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://banktocfo.com",
        "http://localhost:5173",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for file storage
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "service": "BankToCFO API", "version": "1.0.0"}


@app.post("/upload")
async def upload_statement(file: UploadFile = File(...)):
    """
    Upload a bank statement (PDF or CSV) and generate CFO Pack

    Returns:
        job_id: Unique identifier for this processing job
        download_url: URL to download the generated Excel file
    """

    # Validate file type
    allowed_extensions = [".pdf", ".csv"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400, detail="Only PDF and CSV files are supported"
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    try:
        # Save uploaded file
        upload_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Step 1: Parse the CSV
        transactions = parse_bank_statement(upload_path)

        if not transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in file"
            )

        # Step 2: Categorize transactions
        categorized_transactions = categorize_transactions(transactions)

        # Step 3: Generate Excel CFO Pack
        output_path = OUTPUT_DIR / f"{job_id}_CFO_Pack.xlsx"
        generate_cfo_pack(categorized_transactions, output_path)

        # Clean up uploaded file
        upload_path.unlink()

        return {
            "job_id": job_id,
            "status": "completed",
            "transaction_count": len(categorized_transactions),
            "download_url": f"/download/{job_id}",
            "filename": f"CFO_Pack_{datetime.now().strftime('%Y%m%d')}.xlsx",
        }

    except Exception as e:
        # Clean up files on error
        if upload_path.exists():
            upload_path.unlink()

        # Log the full error for debugging
        import traceback

        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())

        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/download/{job_id}")
async def download_cfo_pack(job_id: str):
    """
    Download the generated CFO Pack Excel file
    """
    output_path = OUTPUT_DIR / f"{job_id}_CFO_Pack.xlsx"

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="File not found or expired")

    return FileResponse(
        path=output_path,
        filename=f"CFO_Pack_{datetime.now().strftime('%Y%m%d')}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/status/{job_id}")
async def check_status(job_id: str):
    """
    Check if a CFO Pack is ready for download
    """
    output_path = OUTPUT_DIR / f"{job_id}_CFO_Pack.xlsx"

    return {
        "job_id": job_id,
        "status": "completed" if output_path.exists() else "not_found",
        "ready": output_path.exists(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
