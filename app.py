import streamlit as st
import requests
from datetime import datetime

st.title("Inbound Monitoring Form")

# --- Simulated Database PO Data ---
database_data = {
    "DMI": {
        "4500001234": ["Item A", "Item B", "Item C"],
        "4500005678": ["Item X", "Item Y"],
    },
    "PKS": {
        "4500008888": ["Item D", "Item E"],
    },
    "PMT": {
        "4500009999": ["Item F"],
    },
    "PSM": {
        "4500010000": ["Item G", "Item H"],
    },
    "PST": {
        "4500011111": ["Item J", "Item K", "Item L"],
    },
}

# --- Replace this with your actual Web App URL from Apps Script ---
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyAIfvb09pm4_nLzUukwyGRLN_lG3ZzUyVrn2UCVkfmNDb59CC6M0WOmDLb0tlg1bUMnw/exec"

# Step 1: Select Database
selected_db = st.selectbox("Select Database:", list(database_data.keys()))

# Step 2: Enter PO Number (must match database)
po_number = st.text_input("Insert PO Number:")

# Step 3: Search Button
if st.button("Search"):
    st.session_state.searched_po = po_number
    st.session_state.selected_db = selected_db

# Step 4: Item selection and submission
if "searched_po" in st.session_state and "selected_db" in st.session_state:
    searched_po = st.session_state.searched_po
    selected_db = st.session_state.selected_db

    st.write(f"**Database**: {selected_db}")
    st.write(f"**PO Number**: {searched_po}")

    po_items = database_data[selected_db]

    if searched_po in po_items:
        selected_items = st.multiselect("Select items received", po_items[searched_po])
        qty_dict = {}

        for item in selected_items:
            qty = st.number_input(
                f"Qty received for {item}", min_value=0, step=1, key=f"qty_{item}"
            )
            qty_dict[item] = qty

        if st.button("Submit"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = {
                "entries": [
                    {
                        "timestamp": timestamp,
                        "database": selected_db,
                        "po_number": searched_po,
                        "item": item,
                        "quantity": qty
                    }
                    for item, qty in qty_dict.items() if qty > 0
                ]
            }

            # Send to Google Apps Script
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                if response.status_code == 200:
                    st.success("Data submitted successfully!")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Submission failed: {e}")
    else:
        st.warning("PO not found in selected database.")
