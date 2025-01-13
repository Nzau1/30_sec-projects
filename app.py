import streamlit as st
import pandas as pd
import os
import numpy as np

# Ensure uploads folder exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def main():
    # App Title
    st.title("📊 Excel Search & Analysis System")

    # File uploader with additional details
    uploaded_file = st.file_uploader("Upload Excel File", 
                                     type=["xls", "xlsx"], 
                                     help="Support for .xls and .xlsx files. Max file size: 200MB")

    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load Excel data into a DataFrame
            df = pd.read_excel(file_path)
            
            # Sidebar for additional options
            st.sidebar.header("📋 Data Insights")
            
            # Data Overview
            st.sidebar.subheader("Dataset Overview")
            st.sidebar.write(f"**Total Rows:** {len(df)}")
            st.sidebar.write(f"**Total Columns:** {len(df.columns)}")
            
            # Column Type Analysis
            st.sidebar.subheader("Column Types")
            column_types = df.dtypes
            for col, dtype in column_types.items():
                st.sidebar.text(f"{col}: {dtype}")

            # Main Content
            st.write("### Data Preview")
            st.dataframe(df.head())

            # Search Section
            st.write("### 🔍 Advanced Search Options")
            col1, col2, col3 = st.columns(3)

            with col1:
                search_value = st.text_input("Enter search value", "")
            
            with col2:
                column_options = ["All Columns"] + list(df.columns)
                selected_column = st.selectbox("Select column", column_options)
            
            with col3:
                search_type = st.selectbox("Search Type", [
                    "Contains", 
                    "Exact Match", 
                    "Starts With", 
                    "Ends With"
                ])

            # Additional search options
            col4, col5 = st.columns(2)
            with col4:
                case_sensitive = st.checkbox("Case Sensitive", value=False)
            
            with col5:
                advanced_filtering = st.checkbox("Enable Advanced Filtering")

            # Search Button
            if st.button("Search Data"):
                if search_value:
                    try:
                        # Perform search based on selected type
                        if search_type == "Contains":
                            if selected_column == "All Columns":
                                matches = df[df.apply(
                                    lambda row: row.astype(str).str.contains(
                                        search_value, 
                                        case=case_sensitive, 
                                        na=False
                                    ).any(), 
                                    axis=1
                                )]
                            else:
                                matches = df[df[selected_column].astype(str).str.contains(
                                    search_value, 
                                    case=case_sensitive, 
                                    na=False
                                )]
                        
                        elif search_type == "Exact Match":
                            if selected_column == "All Columns":
                                matches = df[df.apply(
                                    lambda row: (row.astype(str) == search_value).any(), 
                                    axis=1
                                )]
                            else:
                                matches = df[df[selected_column].astype(str) == search_value]
                        
                        elif search_type == "Starts With":
                            if selected_column == "All Columns":
                                matches = df[df.apply(
                                    lambda row: row.astype(str).str.startswith(search_value).any(), 
                                    axis=1
                                )]
                            else:
                                matches = df[df[selected_column].astype(str).str.startswith(search_value)]
                        
                        elif search_type == "Ends With":
                            if selected_column == "All Columns":
                                matches = df[df.apply(
                                    lambda row: row.astype(str).str.endswith(search_value).any(), 
                                    axis=1
                                )]
                            else:
                                matches = df[df[selected_column].astype(str).str.endswith(search_value)]

                        # Display results
                        if not matches.empty:
                            st.success(f"Found {len(matches)} matching row(s):")
                            st.dataframe(matches)
                            
                            # Optional advanced filtering
                            if advanced_filtering and len(matches) > 0:
                                st.write("### 📊 Advanced Filtering")
                                filter_column = st.selectbox("Select column for additional filtering", list(matches.columns))
                                
                                # Numeric columns
                                if pd.api.types.is_numeric_dtype(matches[filter_column]):
                                    min_val, max_val = st.slider(
                                        f"Filter {filter_column}", 
                                        float(matches[filter_column].min()), 
                                        float(matches[filter_column].max()), 
                                        (float(matches[filter_column].min()), float(matches[filter_column].max()))
                                    )
                                    matches = matches[
                                        (matches[filter_column] >= min_val) & 
                                        (matches[filter_column] <= max_val)
                                    ]
                                    st.dataframe(matches)
                        else:
                            st.warning("No matching records found.")
                    
                    except Exception as search_error:
                        st.error(f"Error during search: {search_error}")
                else:
                    st.warning("Please enter a value to search.")

        except Exception as file_error:
            st.error(f"Error processing file: {file_error}")
        
        finally:
            # Optional cleanup or additional processing
            st.sidebar.text("File processing completed")

# Main entry point
if __name__ == "__main__":
    main()