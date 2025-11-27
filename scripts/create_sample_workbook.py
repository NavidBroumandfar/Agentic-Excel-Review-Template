#!/usr/bin/env python3
"""
Create Sample Excel Workbook for Agentic Excel Review Template

This script generates a dummy Excel file with sample review data
for demonstration purposes. No real company data.
"""

import pandas as pd
from pathlib import Path

def create_sample_workbook():
    """Create a sample Excel workbook with dummy review data."""
    
    # Define sample data
    data = {
        'RecordID': [1, 2, 3, 4, 5],
        'Date': [
            '2025-01-15',
            '2025-01-16',
            '2025-01-17',
            '2025-01-18',
            '2025-01-19'
        ],
        'Category': ['Logistics', 'Fulfillment', 'Finance', 'Quality', 'Operations'],
        'ReviewComment': [
            'User reported delay in delivery. Investigation needed.',
            'Incorrect item delivered, replacement scheduled for next week.',
            'Billing discrepancy resolved with credit note issued.',
            'Product quality concern - forwarding to QA team for review.',
            'Process improvement suggested by operations manager.'
        ],
        'Status': ['Open', 'Open', 'Closed', 'Open', 'Open'],
        'Priority': ['Medium', 'High', 'Low', 'High', 'Medium'],
        'Reviewer': ['JDoe', 'ASmith', 'BJones', 'JDoe', 'CWilson']
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Ensure output directory exists
    output_dir = Path('data')
    output_dir.mkdir(exist_ok=True)
    
    # Write to Excel
    output_path = output_dir / 'Sample_Review_Workbook.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='ReviewSheet', index=False)
    
    print(f"✅ Created sample workbook: {output_path}")
    print(f"📊 Sheet: ReviewSheet")
    print(f"📊 Rows: {len(df)}")
    print(f"📊 Columns: {list(df.columns)}")
    
    return output_path

if __name__ == '__main__':
    create_sample_workbook()

