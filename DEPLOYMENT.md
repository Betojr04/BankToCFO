# BankToCFO Backend - Deployment Checklist

## Pre-Deployment Testing

### Local Testing
- [ ] Run `python test_backend.py` - all tests should pass
- [ ] Start server: `python main.py`
- [ ] Visit `http://localhost:8000/docs` - should see API documentation
- [ ] Test upload endpoint with a sample PDF/CSV

### Get OpenAI API Key
- [ ] Go to https://platform.openai.com/api-keys
- [ ] Create new API key
- [ ] Add to `.env` file: `OPENAI_API_KEY=sk-...`
- [ ] Add $5-10 credit to your OpenAI account

## Railway Deployment

### 1. Prepare Repository
```bash
cd banktocfo-backend
git init
git add .
git commit -m "Initial BankToCFO backend"

# Create GitHub repo, then:
git remote add origin https://github.com/yourusername/banktocfo-backend.git
git push -u origin main
```

### 2. Deploy on Railway
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your `banktocfo-backend` repository
- [ ] Railway will auto-detect Python and deploy

### 3. Add Environment Variables
In Railway dashboard → Variables tab, add:

```
OPENAI_API_KEY=sk-your-key-here
CORS_ORIGINS=https://banktocfo.com,http://localhost:5173
```

### 4. Get Your Backend URL
- [ ] After deployment, copy your Railway URL
- [ ] Example: `https://banktocfo-backend-production.up.railway.app`

### 5. Test Deployed Backend
```bash
curl https://your-railway-url.railway.app/
# Should return: {"status":"online","service":"BankToCFO API"}
```

## Lovable Frontend Integration

### 1. Add Backend URL to Lovable
In your Lovable project settings, add environment variable:

```
VITE_API_URL=https://your-railway-url.railway.app
```

### 2. Update Upload Flow Component
Find the `UploadFlow.tsx` component (or wherever the upload happens).

Replace the mock upload code with:

```typescript
const handleUpload = async (file: File) => {
  setIsUploading(true);
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Upload failed');
    }
    
    const data = await response.json();
    
    // Download the CFO Pack
    window.location.href = `${import.meta.env.VITE_API_URL}${data.download_url}`;
    
  } catch (error) {
    console.error('Upload error:', error);
    alert('Upload failed. Please try again.');
  } finally {
    setIsUploading(false);
  }
};
```

### 3. Test Full Flow
- [ ] Upload a PDF bank statement on banktocfo.com
- [ ] Should see processing
- [ ] Should automatically download Excel CFO Pack
- [ ] Open Excel - verify all sheets are present

## Monitoring & Maintenance

### Check Railway Logs
```
Railway Dashboard → Your Project → Deployments → View Logs
```

Look for:
- ✅ Server started successfully
- ✅ PDF processing logs
- ❌ Any errors

### Monitor OpenAI Costs
- [ ] Check https://platform.openai.com/usage
- [ ] Each PDF costs ~$0.01-0.05
- [ ] Set usage alerts if needed

### Test Different Banks
- [ ] Chase PDF
- [ ] Bank of America PDF
- [ ] Wells Fargo PDF
- [ ] Generic CSV
- [ ] Verify all parse correctly

## Optional Enhancements

### Add Supabase Integration (Later)
- [ ] Store user upload history
- [ ] Save generated CFO Packs
- [ ] User authentication

### Add Error Tracking (Later)
- [ ] Set up Sentry for error tracking
- [ ] Add logging to production

### Add Analytics (Later)
- [ ] Track upload success rate
- [ ] Monitor processing time
- [ ] User metrics

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "CORS error" in browser
- Check CORS_ORIGINS includes your Lovable domain
- Restart Railway deployment after changing env vars

### "OpenAI API error"
- Check API key is correct
- Verify you have credits in OpenAI account
- Check rate limits

### "File not found" when downloading
- Files are stored in `/outputs` directory
- May need to configure persistent storage on Railway

## Cost Estimates

### MVP (100 uploads/month)
- Railway: **FREE** (500 hours included)
- OpenAI: **$1-5/month**
- **Total: ~$5/month**

### Scale (1,000 uploads/month)
- Railway: **$5/month** (need paid plan)
- OpenAI: **$10-50/month**
- **Total: ~$20-60/month**

### Enterprise (10,000 uploads/month)
- Railway: **$20/month**
- OpenAI: **$100-500/month**
- **Total: ~$150-550/month**

## Success Criteria

- [ ] Can upload PDF bank statement
- [ ] Backend processes it successfully
- [ ] Excel CFO Pack downloads automatically
- [ ] Excel has all 3 sheets with correct data
- [ ] Charts display properly
- [ ] Categorization is >80% accurate
- [ ] Process takes <30 seconds
- [ ] No errors in Railway logs

## You're Live! 🎉

Once all boxes are checked, BankToCFO is officially launched!

Next: Get your first 10 customers and iterate based on feedback.
