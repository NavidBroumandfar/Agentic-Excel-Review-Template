# UI Module

The Streamlit UI module has been removed to ensure complete anonymization of this template.

If you'd like to build a UI for this system, you can create a simple Streamlit app that:

1. Loads the Excel data using `src/excel/excel_reader.py`
2. Displays KPIs and charts
3. Optionally integrates chat with LM Studio via `src/utils/lmstudio_chat.py`

Example starter:

```python
import streamlit as st
from src.excel.excel_reader import read_review_sheet
from src.utils.config_loader import load_config

st.title("Excel Review Dashboard")

config = load_config()
df, profile = read_review_sheet(config)

st.write(f"Loaded {profile.row_count} rows")
st.dataframe(df.head(10))
```

Run with: `streamlit run your_app.py`

