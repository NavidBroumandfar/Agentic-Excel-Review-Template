# LM Studio Setup & Testing Guide

## Current Status: ❌ **NOT CONNECTED**

LM Studio is not currently running. Follow the steps below to connect it.

---

## Step 1: Start LM Studio

1. **Open LM Studio** on your computer
2. **Load a model** (if you haven't already):
   - Go to the "Chat" or "Local Server" tab
   - Select a model from your downloaded models
   - Make sure a model is loaded

3. **Start the Local Server**:
   - Click on the "Local Server" tab (or "⚙️ Server" button)
   - Click **"Start Server"** button
   - The server should start on `http://127.0.0.1:1234`
   - You should see a message like "Server running on port 1234"

---

## Step 2: Test the Connection

Once LM Studio server is running, test the connection:

```bash
python -m src.utils.lmstudio_smoketest
```

**Expected output when connected:**
```
[SMOKE TEST] Testing connection to: http://127.0.0.1:1234/v1
[OK] Connected to LM Studio
  Response: Hello! I am connected to the Excel Review Agentic Pipeline...
```

---

## Step 3: Run a Full Demo

Once connected, you can test the full Excel Review pipeline:

```bash
# Process 5 sample rows
python src/run_excel_review_demo.py --n 5
```

This will:
- Load data from Quality Review sheet
- Process each row through the LLM
- Generate AI suggestions
- Save results to `out/mtcr_ai_demo.csv`

---

## Troubleshooting

### Connection Refused Error
- **Problem**: `Connection refused` or `target machine actively refused it`
- **Solution**: Make sure LM Studio server is started (see Step 1)

### Wrong Port
- **Problem**: Connection fails but server is running
- **Solution**: Check what port LM Studio is using, then update `config.json`:
  ```json
  {
    "lm_studio_url": "http://127.0.0.1:YOUR_PORT/v1"
  }
  ```

### Model Not Loaded
- **Problem**: Server running but no model loaded
- **Solution**: Load a model in LM Studio before starting the server

---

## Quick Test Commands

```bash
# 1. Test connection
python -m src.utils.lmstudio_smoketest

# 2. Run small demo (5 rows)
python src/run_excel_review_demo.py --n 5

# 3. Run larger demo (10 rows)
python src/run_excel_review_demo.py --n 10
```

