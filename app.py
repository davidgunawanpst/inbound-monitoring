import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# -- CONFIGURE YOUR GOOGLE SHEET HERE --
SHEET_ID = "1viV03CJxPsK42zZyKI6ZfaXlLR62IbC0O3Lbi_hfGRo"
SHEET_NAME = "Master"  # or whatever tab name
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# -- Load data from Google Sheet --
@st.cache_data
def load_po_data():
    df = pd.read_csv(CSV_URL)
    po_dict = {}
    for _, row in df.iterrows():
        db = row['Database']
        po = str(row['Nomor PO'])
        item = row['Item']
        if db not in po_dict:
            po_dict[db] = {}
        if po not in po_dict[db]:
            po_dict[db][po] = []
        po_dict[db][po].append(item)
    return po_dict

database_data = load_po_data()

# --- Replace with your actual Apps Script Webhook URL ---
WEBHOOK_URL = "https://script.google.com/macros/s/your_webhook_id/exec"

# --- UI ---
st.title("Inbound Monitoring Form")

# Step 1: Select Database
selected_db = st.selectbox("Select Database:", list(database_data.keys()))

# Step 2: Select PO Number
po_options = list(database_data[selected_db].keys())
selected_po = st.selectbox("Select PO Number:", po_options)

# Step 3: Select Items and input quantities
item_options = database_data[selected_db][selected_po]
selected_items = st.multiselect("Select items received:", item_options)
qty_dict = {}

for item in selected_items:
    qty = st.number_input(f"Qty received for {item}", min_value=0, step=1, key=f"qty_{item}")
    qty_dict[item] = qty

# Step 4: Submit
if st.button("Submit"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "entries": [
            {
                "timestamp": timestamp,
                "database": selected_db,
                "po_number": selected_po,
                "item": item,
                "quantity": qty
            }
            for item, qty in qty_dict.items() if qty > 0
        ]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            st.success("Data submitted successfully!")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"Submission failed: {e}")
