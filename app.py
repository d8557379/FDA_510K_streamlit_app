
import streamlit as st
import pandas as pd
import requests
import urllib.request
from pathlib import Path
import io
import json
import zipfile
from datetime import datetime

st.set_page_config(page_title="FDA 510K Explorer", layout="wide")
 
# -----------------------------
# Load Data
# -----------------------------
@st.cache_data

#
## Function to load FDA 510k data (simulating st.cache_data for Colab environment)
#def load_fda_data():
#    url = "https://download.open.fda.gov/device/510k/device-510k-0001-of-0001.json.zip"
#
#    # Download the zip file
#    response = requests.get(url)
#    response.raise_for_status() # Raise an exception for HTTP errors
#
#    # Read the zip file content from memory
#    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
#        json_filename = z.namelist()[0]
#        with z.open(json_filename) as f:
#            raw_json_data = json.load(f)
#
#            if 'results' in raw_json_data and isinstance(raw_json_data['results'], list):
#                df_fda_json = pd.DataFrame(raw_json_data['results'])
#            else:
#                print("Warning: 'results' key not found or not a list. Attempting to load entire JSON.")
#                df_fda_json = pd.DataFrame(raw_json_data)
#
#    # Select and rename columns as requested
#    # Note: 'decision_date' is mapped to 'date_received' and 'decision_code' is mapped to 'decision_description'
#    # as these are the available column names in the loaded FDA JSON data.
#    selected_df = df_fda_json[['k_number', 'applicant','device_name', 'contact', 
#        'decision_date', 'date_received','decision_code',
#       'expedited_review_flag','clearance_type', 'product_code']]
## 'statement_or_summary',
#    return selected_df
#
## Load the data
#df = load_fda_data()
## Ensure 'decision_date' and 'date_received' are in datetime format
#df['decision_date'] = pd.to_datetime(df['decision_date'], errors='coerce')
#df['date_received'] = pd.to_datetime(df['date_received'], errors='coerce')
#df = df.sort_values(by="decision_date", ascending=False)
#
#df["Review Time (Days)"] = (df["decision_date"] - df["date_received"]).dt.days
#
#df["year"] = df["date_received"].dt.year

def load_data():
    return pd.read_csv(
         r"https://raw.githubusercontent.com/d8557379/FDA_510K_streamlit_app/main/FDA510k.csv",
        keep_default_na=True,
        encoding="cp1252")
    
df = load_data()
df['decision_date'] = pd.to_datetime(df['decision_date'], errors='coerce')
df['date_received'] = pd.to_datetime(df['date_received'], errors='coerce')
filtered_df = df.copy()   
    
st.title("FDA 510K Explorer")
 
# -----------------------------
# Dynamic Filters for Every Column
# -----------------------------
st.sidebar.header("Filters")


# --- Date Range Filter for 'decision_date' ---
st.sidebar.subheader('Decision Date Filter')

min_decision_date = filtered_df['decision_date'].min().date() if not filtered_df['decision_date'].min() is pd.NaT else datetime.date(1960, 1, 1) # Default min date
max_decision_date = filtered_df['decision_date'].max().date() if not filtered_df['decision_date'].max() is pd.NaT else datetime.date.today() # Default max date

start_decision_date = st.sidebar.date_input('Start Decision Date', value=None, key='start_decision_date')
end_decision_date = st.sidebar.date_input('End Decision Date', value=max_decision_date, key='end_decision_date')

# Apply decision date filter
if start_decision_date and end_decision_date:
    filtered_df = filtered_df[
        (filtered_df['decision_date'].dt.date >= start_decision_date) &
        (filtered_df['decision_date'].dt.date <= end_decision_date)
    ]

# --- Date Range Filter for 'date_received' ---
st.sidebar.subheader('Date Received Filter')
min_received_date = filtered_df['date_received'].min().date() if not filtered_df['date_received'].min() is pd.NaT else datetime.date(1960, 1, 1) # Default min date
max_received_date = filtered_df['date_received'].max().date() if not filtered_df['date_received'].max() is pd.NaT else datetime.date.today() # Default max date

start_received_date = st.sidebar.date_input('Start Received Date', value=None, key='start_received_date')
end_received_date = st.sidebar.date_input('End Received Date', value=max_received_date, key='end_received_date')

# Apply received date filter
if start_received_date and end_received_date:
    filtered_df = filtered_df[
        (filtered_df['date_received'].dt.date >= start_received_date) &
        (filtered_df['date_received'].dt.date <= end_received_date)
    ]

# --- Dynamic Filtering for other columns ---
for col in df.columns:
    # Skip columns that are not suitable for general filtering or already handled by date filters
    if col in ['decision_date', 'date_received']:
        continue

    unique_values = sorted(filtered_df[col].dropna().astype(str).unique())
 
    if len(unique_values) <= 20:
        selected = st.sidebar.multiselect(
            f"Select {col}",
            unique_values,
            default=[],
            key=f'multiselect_{col}'
        )
 
        if selected:
            filtered_df = filtered_df[
                filtered_df[col].astype(str).isin(selected)
            ]
 
    else:
        text_filter = st.sidebar.text_input(
            f"Filter {col} contains",
            key=f'text_filter_{col}'
        )
 
        if text_filter:
            filtered_df = filtered_df[
                filtered_df[col]
                .astype(str)
                .str.contains(text_filter, case=False, na=False)
            ]
 
st.sidebar.markdown("---")
st.sidebar.subheader("Reset Filters")
 

# Initialize defaults
if "applicant" not in st.session_state:
    st.session_state["applicant"] = ""

if "k_number" not in st.session_state:
    st.session_state["k_number"] = ""


# Reset button
if st.sidebar.button("Reset Filters"):
    st.session_state["applicant"] = ""
    st.session_state["k_number"] = ""
    st.rerun()


st.sidebar.markdown("---")
st.sidebar.subheader("Quick Filters")

# Quick filter buttons for specific applicants
if st.sidebar.button("Applicant: Abbott"):
    st.session_state["applicant"] = "Abbott"
    st.rerun()

if st.sidebar.button("Applicant: Roche"):
    st.session_state["applicant"] = "Roche"
    st.rerun()

if st.sidebar.button("Applicant: Abbott Laboratories"):
    st.session_state["applicant"] = "Abbott Laboratories"
    st.rerun()

# Use the value from st.session_state for filtering
applicant_filter_value = st.session_state.get("applicant", "")


if applicant_filter_value:
    # This part assumes 'filtered_df' is already defined and accessible.
    # If not, this code would raise a NameError.
    # Ensure 'filtered_df' is initialized before this block, e.g., filtered_df = initial_dataframe.
    # For the purpose of indentation, I will re-indent it as if 'filtered_df' exists.
    if 'filtered_df' in locals() or 'filtered_df' in globals(): # Placeholder for context
        filtered_df = filtered_df[
            filtered_df["applicant"]
            .fillna("")
            .str.contains(applicant_filter_value, case=False, na=False)
        ]

# Use the value from st.session_state for filtering
kumber_filter_value = st.session_state.get("k_number", "")

# This part assumes 'filtered_df' exists and has a 'k_number' column if the condition is met.
# Also assuming filtered_df is updated by the applicant filter before this block.
if "k_number" in filtered_df.columns and kumber_filter_value:
    filtered_df = filtered_df[
        filtered_df["k_number"]
        .fillna("")
        .str.contains(kumber_filter_value, case=False, na=False)
    ] 

# Format the datetime objects to display only the date part (YYYY-MM-DD)
df['date_received'] = df['date_received'].dt.strftime('%Y-%m-%d-%Y')
df['decision_date'] = df['decision_date'].dt.strftime('%Y-%m-%d')

# -----------------------------
# Display Results
# -----------------------------
st.subheader("Filtered 510K Records")
 
st.write(f"Records found: {len(filtered_df):,}")
 
st.dataframe(
    filtered_df.drop(columns=["year"]),
    height=600,
    width="content",
    hide_index=True
)
# 
## -----------------------------
## Build FDA PDF Links
## -----------------------------
#st.subheader("FDA 510K Documents")
# 
#docs = ["A", "B", "C"]
#mapping = {'A': 'Approval Order', 'B': 'Summary', 'C': 'Labeling'}
#
#if "KNUMBER" in filtered_df.columns and "year" in filtered_df.columns:
# 
#    pdf_rows = []
# 
#    unique_df = (
#        filtered_df[["KNUMBER", "year"]]
#        .drop_duplicates()
#        .reset_index(drop=True)
#    )
#
#
#    for _, row in unique_df.iterrows():
# 
#        510k = str(row["KNUMBER"])
#        
#        yr=int(str(row["year"]))
#        if yr < 2002:
#            year2 = ""
#        else:
#            year2 = str(int(str(row["year"])[-2:]))
#        
#        
#
#        for doc in docs:
#            url = (
#            f"https://www.accessdata.fda.gov/cdrh_docs/pdf{year2}/"
#            f"{510k}{doc}.pdf"
#            )
#            
#            fallback_url = (f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?ID={pma}")
#            
#            pdf_rows.append({
#            "PMANUMBER": pma,
#            "Document": doc,
#            "PDF Link": url,
#            "Verified Link": fallback_url
#                })
#    
#    pdf_df = pd.DataFrame(pdf_rows)
#    pdf_df['Document Name'] = pdf_df['Document'].map(mapping)
#    
#st.dataframe(
#    pdf_df[['PMANUMBER','Document Name', 'PDF Link', "Verified Link"]].drop_duplicates(),
#    width='stretch',
#    column_config={
#        "PDF Link": st.column_config.LinkColumn(
#            "PDF Link",
#            display_text=r".*/([^/]+\.pdf)$"
#        ),
#        "Verified Link": st.column_config.LinkColumn(
#            "Verified Link",
#            display_text=r".*ID=([^/]+)"
#        )
#    },
#    hide_index=True
#)
# 
## -----------------------------
## Download PDFs as ZIP
## -----------------------------
#
#
#st.subheader("Download PDFs")
#
#if st.button("Prepare ZIP of All Visible PDFs"):
#	progress = st.progress(0)
#	
#	zip_buffer = io.BytesIO()
#	
#	total = len(pdf_rows)
#	
#	if total == 0:
#		st.warning("No PDFs found to prepare in the ZIP.")
#	else:
#		with zipfile.ZipFile(
#			zip_buffer,
#			mode="w",
#			compression=zipfile.ZIP_DEFLATED,
#		) as zip_file:
#			
#			for i, row in enumerate(pdf_rows):
#				
#				url = row["PDF Link"]
#				
#				filename = (
#					f"{row['PMANUMBER']}"
#					f"{row['Document']}.pdf"
#				)
#				
#				st.write(f"Attempting to download: {filename} from {url}") # Debugging line
#				try:
#					r = requests.get(url, timeout=30)
#					
#					if r.status_code == 200:
#						zip_file.writestr(
#							filename,
#							r.content,
#						)
#						st.write(f"Successfully added {filename} to ZIP.") # Debugging line
#					else:
#						st.warning(f"Failed to download {filename} (Status: {r.status_code}).") # Debugging line
#					
#				except requests.exceptions.RequestException as e:
#					st.error(f"Error downloading {filename} from {url}: {e}") # Debugging line
#				except Exception as e:
#					st.error(f"An unexpected error occurred for {filename}: {e}") # Debugging line
#			
#				progress.progress((i + 1) / total)
#				
#		zip_buffer.seek(0)
#		
#		st.success(
#			f"ZIP prepared with up to {total} PDFs."
#		)
#		
#	
#	st.download_button(
#		label="Download ZIP",
#		data=zip_buffer,
#		file_name="pma_pdfs.zip",
#		mime="application/zip",
#		key="download_zip_button" # Added unique key
#	)