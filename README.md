# BankToCFO Backend

FastAPI backend for BankToCFO - converts bank statements (PDF/CSV) into professional CFO Packs.

## Features

- ✅ PDF statement parsing using OpenAI Vision API
- ✅ CSV statement parsing (Chase, BofA, Wells Fargo, Generic)
- ✅ Automatic transaction categorization
- ✅ Excel CFO Pack generation with:
  - Clean transactions tab
  - Monthly cash flow summary
  - Category breakdown
  - Charts and visualizations

## Local Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run Locally

```bash
python main.py
```

API will be available at `http://localhost:8000`

API docs at `http://localhost:8000/docs`

## API Endpoints

### `POST /upload`
Upload a bank statement (PDF or CSV)

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@statement.pdf"
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "transaction_count": 45,
  "download_url": "/download/abc123",
  "filename": "CFO_Pack_20240118.xlsx"
}
```

### `GET /download/{job_id}`
Download the generated CFO Pack Excel file

### `GET /status/{job_id}`
Check if CFO Pack is ready

## Deploy to Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repo-url
git push -u origin main
```

### 2. Deploy on Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `CORS_ORIGINS`: `https://banktocfo.com`

5. Railway will auto-deploy

### 3. Get Your Backend URL

After deployment, Railway will give you a URL like:
```
https://banktocfo-backend-production.up.railway.app
```

### 4. Update Lovable Frontend

In your Lovable project, add environment variable:

```
VITE_API_URL=https://your-railway-url.railway.app
```

Then update your frontend upload code to use this URL.

## Frontend Integration

### Example Upload Code (React)

```javascript
const uploadStatement = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  // Download the CFO Pack
  window.location.href = `${import.meta.env.VITE_API_URL}${data.download_url}`;
};
```

## Cost Estimates

### OpenAI Vision API Costs
- **Model:** GPT-4 Vision (gpt-4o)
- **Cost:** ~$0.01-0.05 per PDF statement (depending on pages)
- **100 statements/month:** ~$1-5/month
- **1,000 statements/month:** ~$10-50/month

You can reduce costs by:
1. Caching results for duplicate uploads
2. Using lower resolution images
3. Falling back to PDF extraction libraries for simple statements

## File Structure

```
banktocfo-backend/
├── main.py                    # FastAPI app
├── services/
│   ├── parser.py              # Routes to PDF/CSV parsers
│   ├── pdf_parser.py          # PDF → transactions using AI
│   ├── categorizer.py         # Transaction categorization
│   └── excel_generator.py     # Excel CFO Pack creation
├── uploads/                   # Temporary file storage
├── outputs/                   # Generated Excel files
├── requirements.txt
├── .env.example
└── railway.json              # Railway deployment config
```

## Next Steps

### Phase 2 Enhancements
- [ ] User authentication (integrate with Supabase)
- [ ] Save upload history per user
- [ ] Support multiple months in one upload
- [ ] Custom category rules per user
- [ ] Webhook notifications when processing complete
- [ ] Background task processing (Celery/Redis)

### Phase 3 Scale
- [ ] Rate limiting
- [ ] File size limits
- [ ] Caching layer (Redis)
- [ ] Database for metadata
- [ ] Admin dashboard
