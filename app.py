import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from io import BytesIO
import base64

def safe_dataframe(df):

    df = df.copy()

    for col in df.columns:

        try:
            df[col] = df[col].astype(str)

        except Exception:
            pass

    return df.fillna("")

# App title and configuration
st.set_page_config(page_title="CSV Explorer Pro", layout="wide")
st.title("📊 CSV Explorer Pro")
st.markdown("A powerful tool to explore, analyze, and transform your CSV data.")

# Sidebar
with st.sidebar:
    st.header("🔄 Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        st.markdown("---")
        st.subheader("⚙️ Settings")
        sample_size = st.slider("Preview sample size", 100, 1000, 100)
    
    st.markdown("---")
    st.caption("Built with ❤️ using Python + Streamlit")

def get_download_link(df, filename, text):
    """Generate a download link for the dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def plot_column_distribution(df, column):

    numeric_data = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    # Numeric chart
    if numeric_data.notnull().sum() > 0:

        fig = px.histogram(
            x=numeric_data,
            title=f"Distribution of {column}"
        )

    # Categorical chart
    else:

        value_counts = (
            df[column]
            .astype(str)
            .value_counts()
            .head(20)
        )

        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Distribution of {column}"
        )

    return fig

if uploaded_file:
    try:
        # Read the CSV file
        # Read CSV
        df = pd.read_csv(uploaded_file)

        # Make dataframe fully safe
        df = safe_dataframe(df)
        
        # File Overview
        st.subheader("📋 File Overview")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🧾 Rows", f"{df.shape[0]:,}")
        col2.metric("📁 Columns", f"{df.shape[1]:,}")
        mem_usage = df.memory_usage(deep=True).sum() / 1024**2
        col3.metric("💾 Memory Usage", f"{mem_usage:.2f} MB")
        col4.metric("🔢 Numeric Columns", f"{df.select_dtypes(include=['int64', 'float64']).columns.size}")

        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Data Explorer",
            "📊 Visualizations",
            "📈 Analysis",
            "🧹 Data Cleaning",
            "⬇️ Export"
        ])

        with tab1:
            st.subheader("Data Preview")
            
            # Column filter
            selected_columns = st.multiselect("Select columns to display", df.columns.tolist(), default=df.columns.tolist())
            filtered_df = df[selected_columns]
            
            # Search filter
            search_term = st.text_input("Search in data")
            if search_term:
                filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
            
            st.dataframe(filtered_df.head(sample_size), use_container_width=True)

        with tab2:
            st.subheader("Data Visualization")
            
            # Column selection for visualization
            viz_col = st.selectbox("Select column to visualize", df.columns)
            if viz_col:
                st.plotly_chart(plot_column_distribution(df, viz_col), use_container_width=True)
                
                # Correlation matrix for numeric columns
                if len(df.select_dtypes(include=['int64', 'float64']).columns) > 1:
                    st.subheader("Correlation Matrix")
                    corr_matrix = df.select_dtypes(include=['int64', 'float64']).corr()
                    fig = px.imshow(corr_matrix, title="Correlation Matrix")
                    st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("Data Analysis")
            
            # Basic statistics
            st.write("Summary Statistics:")
            summary_df = df.describe(include='all').astype(str)

            st.dataframe(
                safe_dataframe(summary_df),
                use_container_width=True
            )
            
            # Column info
            st.write("Column Information:")
            col_info = pd.DataFrame({
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.dataframe(col_info, use_container_width=True)

        with tab4:
            st.subheader("Data Cleaning")
            
            # Missing values handling
            st.write("Missing Values:")
            missing_df = df.isnull().sum().to_frame(name="Missing Count")
            missing_df['Percentage'] = (missing_df['Missing Count'] / len(df) * 100).round(2)
            st.dataframe(missing_df, use_container_width=True)
            
            # Duplicate handling
            st.write("Duplicate Rows:", df.duplicated().sum())
            
            # Clean data preview
            if st.button("Generate Clean Dataset"):
                cleaned_df = df.dropna().drop_duplicates()
                st.write(f"Cleaned data shape: {cleaned_df.shape}")
                st.dataframe(cleaned_df.head(sample_size), use_container_width=True)
                st.markdown(get_download_link(cleaned_df, "cleaned_data.csv", "📥 Download Cleaned Data"), unsafe_allow_html=True)

        with tab5:
            st.subheader("Export Options")
            
            # Export original data
            st.markdown(get_download_link(df, "original_data.csv", "📥 Download Original Data"), unsafe_allow_html=True)
            
            # Export selected columns
            if len(selected_columns) < len(df.columns):
                st.markdown(get_download_link(filtered_df, "filtered_data.csv", "📥 Download Filtered Data"), unsafe_allow_html=True)
            
            # Export summary statistics
            summary_stats = df.describe(include='all')
            st.markdown(get_download_link(summary_stats, "summary_statistics.csv", "📥 Download Summary Statistics"), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        st.info("Please make sure your CSV file is properly formatted and try again.")
else:
    st.info("👆 Please upload a CSV file to begin exploring your data!")
    
    # Sample features showcase
    st.markdown("""
    ### 🌟 Features:
    - 📊 Interactive data visualization
    - 🔍 Advanced filtering and search
    - 📈 Statistical analysis
    - 🧹 Data cleaning tools
    - ⬇️ Multiple export options
    
    Upload a CSV file to get started!
    """)
