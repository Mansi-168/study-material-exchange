import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SHEET_NAME = "Datasheet" 

# Define the scope for accessing Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from the JSON file
import os
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# Load credentials from environment variable
credentials_json = os.getenv("GCP_CREDENTIALS")
credentials_dict = json.loads(credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open(SHEET_NAME).sheet1

# Streamlit UI
st.title("Exchange Platform for Study Materials")
st.write("Seniors can list their materials, and juniors can buy them at a lower price.")

# Form to list items
st.header("List an Item for Sale")
with st.form(key="listing_form"):
    name = st.text_input("Your Name")
    item = st.selectbox("Item Type", ["Calculator", "Lab File", "Textbook"])
    description = st.text_area("Item Description")
    price = st.number_input("Selling Price (INR)", min_value=0)
    contact = st.text_input("Your Contact (Email/Phone)")
    submit = st.form_submit_button("Submit Listing")

    if submit:
        if name and item and description and price and contact:
            sheet.append_row([name, item, description, price, contact])
            st.success("Your item has been listed successfully!")
            st.rerun()  # ✅ Correct method

        else:
            st.warning("Please fill all fields.")

# Display available items
st.header("Available Items")
data = sheet.get_all_records(expected_headers=["Name", "Item", "Description", "Price", "Contact"])

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)  # Display as a DataFrame
else:
    st.write("No items available yet. Check back later!")
