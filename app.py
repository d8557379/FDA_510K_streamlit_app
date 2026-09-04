
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
page = st.sidebar.radio("FDA Database", ["CDRH 510(k)", "CBER Biological 510(k)"]
)
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

if page == "CBER Biological 510(k)":

    st.title("FDA CBER Biological 510(k) Explorer")

    cber_links = pd.DataFrame(
        {
            "Year": [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017],
            "FDA Page": [
                "https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2026",
                "https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2025",
                "https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2024",
                "https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2023",
                "https://web.archive.org/web/20240417025726/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2022",
                "https://web.archive.org/web/20240519015307/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2021",
                "https://web.archive.org/web/20221128045708/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2020",
                "https://web.archive.org/web/20240415164859/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2019",
                "https://web.archive.org/web/20231204041947/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2018",
                "https://web.archive.org/web/20240415163025/https://www.fda.gov/vaccines-blood-biologics/substantially-equivalent-510k-device-information/cleared-510k-submissions-supporting-documents-2017",

                              
            ]
        }
    )

    selected_year = st.selectbox(
        "Select Year",
        sorted(cber_links["Year"], reverse=True)
    )

    url = cber_links.loc[
        cber_links["Year"] == selected_year,
        "FDA Page"
    ].iloc[0]
    
    try:
        tables = pd.read_html(url)

        if tables:
            st.subheader(f"{selected_year} FDA Biological 510(k) Clearances")
            st.dataframe(
                tables[0],
                height=600,
                use_container_width=True
            )
        else:
            st.warning("No table found for this year.")

    except Exception as e:
        st.error(f"Unable to load FDA data: {e}")

    st.subheader("FDA Cleared 510(k) Submissions with Supporting Documents")
    st.dataframe(
        cber_links,
        column_config={
            "FDA Page": st.column_config.LinkColumn("FDA Page", display_text=r"Supporting Documents")
        },
        hide_index=True,
        use_container_width=True
            )

    st.stop()
        
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
 
    if len(unique_values) <= 30:
        selected = st.sidebar.multiselect(
            f"{col}",
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
            f"{col} contains",
            key=f'text_filter_{col}'
        )
 
        if text_filter:

            filtered_df = filtered_df[filtered_df[col]
                .astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .str.contains(text_filter.strip(), case=False, na=False)
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
    st.session_state["device_name"] = ""
    st.session_state["contact"] = ""
    st.session_state["decision_date"] = ""
    st.session_state["date_received"] = ""
    st.session_state["expedited_review_flag"] = ""
    st.session_state["clearance_type"] = ""
    st.session_state["product_code"] = ""

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
# -----------------------------
# Build FDA PDF Links
# -----------------------------
st.subheader("FDA 510K Documents")

docs = ["A"]
mapping = {'A': 'Summary'}

if "k_number" in filtered_df.columns and "year" in filtered_df.columns:

   pdf_rows = []

   unique_df = (
       filtered_df[["k_number","applicant", "year"]]
       .drop_duplicates()
       .reset_index(drop=True)
   )


   for _, row in unique_df.iterrows():

       pmn = str(row["k_number"])

       yr=int(str(row["year"]))
       if yr < 2002:
           year2 = ""
       else:
           year2 = str(int(str(row["year"])[-2:]))



       for doc in docs:
           url1 = (
           f"https://www.accessdata.fda.gov/cdrh_docs/pdf{year2}/"
           #f"https://www.accessdata.fda.gov/cdrh_docs/reviews/"
           f"{pmn}.pdf"
           )
           url2 = (
           f"https://www.accessdata.fda.gov/cdrh_docs/reviews/"
           f"{pmn}.pdf"
           )


           if pmn.startswith("DEN"):
               fallback_url = ("https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm?ID="f"{pmn}")
               summary_value = url2
           else:
               fallback_url = ("https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID="f"{pmn}")
               summary_value = url1

           pdf_rows.append({
           "K_Number": pmn,
            "Applicant Name": row["applicant"],
           "Summary": url1,
           "Decision Summary": url2,
           "FDA Source": fallback_url
               })
   pdf_df = pd.DataFrame(pdf_rows)

st.dataframe(
   pdf_df[['K_Number',"Applicant Name",'Summary', 'Decision Summary', "FDA Source"]].drop_duplicates(),
   width='stretch',
   column_config={
       "Summary": st.column_config.LinkColumn(
           "Summary",
           display_text=r".*/([^/]+\.pdf)$"
       ),
        "Decision Summary": st.column_config.LinkColumn(
        "Decision Summary",
           display_text=r".*/([^/]+\.pdf)$"
       ),
       "FDA Source": st.column_config.LinkColumn(
           "FDA Source",
           display_text=r".*ID=([^/]+)"
       )
   },
   hide_index=True
)

# -----------------------------
# Download PDFs as ZIP
# -----------------------------

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
st.subheader("Download PDFs")

if st.button("Prepare ZIP of All Visible PDFs"):

    progress_text = st.empty()
    progress_bar = st.progress(0)
    zip_buffer = io.BytesIO()

    total_pdfs = len(pdf_rows)+1
    
    if total_pdfs == 0:
        st.warning("No PDFs found to prepare in the ZIP.")

    else:
        with zipfile.ZipFile(
            zip_buffer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:

            for i, row in enumerate(pdf_rows):
                current_progress = (i + 1) / total_pdfs
                progress_text.text(f"Downloading PDF {i + 1} of {total_pdfs}: {row['K_Number']}.pdf")
                progress_bar.progress(current_progress)                

                pmn = row["K_Number"]  # Example: K252424

                # Extract year from PMN if available
  
                year2 = pmn[1:3]

                url1 = row["Summary"]

                url2 = row["Decision Summary"]

                urls_to_try = [
                    ("summary", url1),
                    ("decision_summary", url2),
                ]

                for source_name, url in urls_to_try:

                    filename = f"{pmn}_{source_name}.pdf"

                    st.write(
                        f"Attempting: {filename} from {url}"
                    )
                    try:
                        r = requests.get(url, timeout=30, headers=headers)
                        
                        if r.status_code == 200:
                            zip_file.writestr(
                                filename,
                                r.content,
                            )
                            st.info(f"Successfully added {filename} to ZIP.")
                        else:
                            st.warning(f"Failed to download {filename} (Status: {r.status_code}).")
                        
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error downloading {filename} from {url}: {e}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred for {filename}: {e}")

           
        zip_buffer.seek(0)
        progress_text.empty() # Clear progress text
        progress_bar.empty() # Clear progress bar

        st.success(
            f"ZIP prepared with {total_pdfs} PDFs. Click the button below to download."
        )
        
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="510k_pdfs.zip",
            mime="application/zip",
            key="download_zip_button"
        )