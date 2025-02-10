import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
SHEET_NAME = "Datasheet"

# Define the scope for accessing Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Initialize connection to Google Sheets
def init_google_sheets():
    try:
        credentials = st.secrets["google"]  # ✅ Fetch Google Sheets credentials
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

# Initialize the sheet
sheet = init_google_sheets()

# Streamlit UI
st.title("Exchange Platform for Study Materials")
st.write("Seniors can list their materials, and juniors can buy them at a lower price.")

if sheet is not None:
    # Form to list items
    st.header("List an Item for Sale")
    with st.form(key="listing_form"):
        name = st.text_input("Your Name")
        item = st.selectbox("Item Type", ["Calculator", "Lab File", "Textbook"])
        description = st.text_area("Item Description")
        original_price = st.number_input("Original Price (INR)", min_value=0)

        if original_price > 0:
            suggested_seller_price = 0.4 * original_price  # 40% of original price
            st.write(f"⚠️ Since the product is used, we will buy it for **INR {suggested_seller_price:.2f}** (40% of the original price).")
            agree_to_sell = st.checkbox("I agree to sell at this price")

        contact = st.text_input("Your Contact (Email/Phone)")
        submit = st.form_submit_button("Submit Listing")
        
        if submit:
            if name and item and description and original_price and contact and agree_to_sell:
                buyer_price = 0.45 * original_price  # Buyer will see 45% of the original price
                
                try:
                    sheet.append_row([name, item, description, suggested_seller_price, buyer_price, contact])
                    st.success("Your item has been listed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding item: {str(e)}")
            else:
                st.warning("Please fill all fields and agree to the selling price.")

    # Display available items
    st.header("Available Items")
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)

            # Check if 'Item' column exists (prevents crashes)
            if "Item" not in df.columns:
                st.error("Error: 'Item' column not found in Google Sheets data.")
            else:
                # Search functionality
                search_term = st.text_input("Search items")
                if search_term:
                    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

                # Filter functionality
                item_type = st.multiselect("Filter by Item Type", options=df["Item"].unique())  # ✅ FIXED COLUMN NAME
                if item_type:
                    df = df[df["Item"].isin(item_type)]
                
                # Show buyer price instead of seller price
                df = df.rename(columns={"Buyer Price": "Price (INR)"})  # Rename for clarity
                
                st.dataframe(df[["Item", "Description", "Price (INR)", "Contact"]])
        else:
            st.write("No items available yet. Check back later!")
    except Exception as e:
        st.error(f"Error fetching items: {str(e)}")
else:
    st.error("Could not connect to Google Sheets. Please check your credentials.")
