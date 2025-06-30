import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Reily Circana File Cleaner", layout="centered")

st.title("🧼 Reily Circana File Cleaner")
st.write("""
Welcome to the **Reily Circana File Cleaner**.  
Upload your **raw Circana CSV file** below. The app will process, clean, and prepare it for Looker Studio.
""")

# Upload file
uploaded_file = st.file_uploader("📤 Upload Reily Circana CSV File", type=["csv"])

if uploaded_file:
    try:
        # Load CSV
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        df["End Date MM/dd/yyyy"] = pd.to_datetime(df["End Date MM/dd/yyyy"])

        # Aggregate totals
        numeric_cols = [
            "Sales Units", "Sales Amount", "Store On Hand Units Ending",
            "DC On Hand Units Ending", "Promo Sales Units", "Total Returns Units",
            "Number of Listed Clubs", "Unique Stores Selling", "Out of Stock Clubs"
        ]
        totals = df.groupby("End Date MM/dd/yyyy")[numeric_cols].sum().reset_index()
        totals["Product"] = "Total"
        totals["Time"] = "Total"
        totals["Article Nbr"] = ""
        totals["Primary DC Nbr"] = ""

        final_cols = [
            "Product", "Time", "Article Nbr", "Primary DC Nbr", "Sales Units", "Sales Amount",
            "Store On Hand Units Ending", "DC On Hand Units Ending", "Promo Sales Units",
            "Total Returns Units", "End Date MM/dd/yyyy", "Unique Stores Selling",
            "Number of Listed Clubs", "Out of Stock Clubs"
        ]
        totals = totals[final_cols]
        totals = totals[df.columns]

        df_with_totals = pd.concat([df, totals], ignore_index=True)
        df_with_totals.sort_values(by="End Date MM/dd/yyyy", inplace=True)

        # Add Item Ranking
        item_rankings = {
            "WF COLOMBIAN GROUND COFFEE 40 OZ - 322314": 1,
            "WF COLOMBIAN WHOLE BEAN, 8 - 40 OZ - 322416": 2,
            "WF DONUT SHOP GROUND 40 OZ - 322317": 3,
            "WF FRENCH ROAST GROUND 40 OZ - 322318": 4,
            "WF FRENCH ROAST WHOLE BEAN, 8 - 40 OZ - 322315": 5,
            "WF CARAMEL GROUND COFFEE 32 OZ - 322316": 6,
            "NEC BREAKFAST BLEND GROUND 40OZ - 341672": 7,
            "NEW ENGLAND COFFEE BUTTER PECAN GRND40OZ - 330275": 8,
            "Total": 9
        }
        df_with_totals["Item Ranking"] = df_with_totals["Product"].map(item_rankings).astype("Int64")

        # Add 'Is Latest'
        latest_date = df_with_totals["End Date MM/dd/yyyy"].max()
        df_with_totals["Is Latest"] = (df_with_totals["End Date MM/dd/yyyy"] == latest_date).astype(int)

        # Reorder columns
        ordered_columns = [
            "Product", "Time", "Article Nbr", "Primary DC Nbr",
            "Sales Units", "Sales Amount", "Store On Hand Units Ending", "DC On Hand Units Ending",
            "Promo Sales Units", "Total Returns Units", "End Date MM/dd/yyyy", "Item Ranking",
            "Unique Stores Selling", "Number of Listed Clubs", "Out of Stock Clubs", "Is Latest"
        ]
        df_with_totals = df_with_totals[ordered_columns]

        # Show preview
        st.success("✅ File processed successfully. Here's a preview:")
        st.dataframe(df_with_totals.head())

        # Download cleaned file
        cleaned_csv = df_with_totals.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Cleaned Reily Circana File",
            data=cleaned_csv,
            file_name="reily_cleaned_circana_data.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ An error occurred while processing: {e}")
