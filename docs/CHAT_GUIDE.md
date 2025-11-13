# Chat with MTCR Agent LLM - User Guide

You can chat with the same LLM model used by the MTCR agent in two ways:

---

## 🖥️ Option 1: Terminal Chat (Recommended for Testing)

### Setup:
1. Make sure LM Studio server is running:
   - Open LM Studio
   - Go to "Local Server" tab
   - Click "Start Server" (should show "Server running on port 1234")

2. Run the chat script:
   ```bash
   python src/utils/lmstudio_chat.py
   ```

### Usage:
- Type your message and press Enter
- The LLM will respond
- Type `quit` or `exit` to end the chat
- Type `clear` to clear conversation history
- Press `Ctrl+C` to exit anytime

### Example:
```
You: What is SOP 029014?
Assistant: SOP 029014 is the Technical Complaint Review procedure...

You: How should I handle a missing calibration certificate?
Assistant: According to SOP 029014, a missing calibration certificate...
```

---

## 💻 Option 2: LM Studio Built-in Chat

### Setup:
1. Open LM Studio application
2. Make sure a model is loaded
3. Go to the "Chat" tab
4. Start chatting!

### Usage:
- Just type in the chat box and press Enter
- The same model used by the MTCR agent will respond
- No special commands needed

---

## 🔗 Connection Details

Both methods connect to the **same LLM model** at:
- **Endpoint:** `http://127.0.0.1:1234/v1`
- **Model:** The model loaded in LM Studio
- **Connection:** Same as the MTCR agent uses

---

## 📝 Important Notes

### What's the Same:
- ✅ Same LLM model
- ✅ Same endpoint
- ✅ Same capabilities

### What's Different:
- **Chat interfaces:** General conversation (no MTCR-specific prompts)
- **MTCR Agent:** Automatically adds:
  - SOP 029014 context
  - Quality Review formatting
  - Standardized reason taxonomy
  - Confidence scoring

### When to Use Each:

**Terminal Chat:**
- Testing the LLM connection
- Quick questions
- General conversation
- Debugging

**LM Studio Chat:**
- Visual interface
- Chat history in UI
- Model management
- Easy to use

**MTCR Agent (run_mtcr_demo.py):**
- Processing Quality Review comments
- Generating standardized suggestions
- Full agentic pipeline with RAG
- Production use

---

## 🐛 Troubleshooting

### "Cannot connect to LM Studio"
- Make sure LM Studio server is running
- Check that the server is on port 1234
- Verify the model is loaded

### "Connection refused"
- Start the server in LM Studio (Local Server tab → Start Server)
- Wait a few seconds for it to initialize

### Script doesn't work
- Make sure you're in the project root directory
- Check that `config.json` exists (or it will use default URL)
- Verify Python can import `requests` library

---

## 🎯 Quick Start

1. **Start LM Studio server:**
   ```
   LM Studio → Local Server → Start Server
   ```

2. **Test connection:**
   ```bash
   python -m src.utils.lmstudio_smoketest
   ```

3. **Start chatting:**
   ```bash
   python src/utils/lmstudio_chat.py
   ```

Enjoy chatting with your MTCR agent's LLM! 🚀

