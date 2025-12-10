"""
Vector Search Application - Streamlit UI
Provides customer-facing interface for vector ingestion and similarity search
"""

import streamlit as st  # type: ignore[import-untyped]
import prestodb
from prestodb.exceptions import PrestoUserError
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import json
import csv
import os
import time
from typing import List, Tuple, Optional, cast
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Page configuration
st.set_page_config(
    page_title="Similarity Search System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* 0. IBM Plex Sans Font Import */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');
    
    /* Apply IBM Plex Sans to the entire app */
    .stApp {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .result-card {
        background-color: #fffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'ingestion_complete' not in st.session_state:
    st.session_state.ingestion_complete = False

# Helper Functions
@st.cache_resource
def load_embedding_model(model_name: str):
    """Load and cache the embedding model"""
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

def get_presto_connection(host: str, port: int, user: str, catalog: str, schema: str,
                          http_scheme: str = 'http', principal_id: str = "", password: str = "",
                          disable_ssl_verification: bool = False):
    """Create Presto connection with optional basic authentication and SSL verification control"""
    try:
        # Build connection parameters
        conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'catalog': catalog,
            'schema': schema,
            'http_scheme': http_scheme,
        }
        
        # Add basic authentication if credentials provided
        if principal_id and password:
            conn_params['auth'] = prestodb.auth.BasicAuthentication(principal_id, password)
        
        conn = prestodb.dbapi.connect(**conn_params)
        
        # Disable SSL verification if requested (for self-signed certificates)
        if disable_ssl_verification and http_scheme == 'https':
            conn._http_session.verify = False
        
        return conn
    except Exception as e:
        raise PrestoUserError(f"Connection Error: {e}")

def execute_query(conn, sql: str, fetch: bool = False):
    """Execute SQL query"""
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        if fetch:
            return cursor.fetchall(), cursor.description
        return None, None
    except Exception as e:
        st.error(f"Query Failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()

def embed_text(model, text: str) -> str:
    """Generate embedding for input text"""
    embedding = model.encode(text, normalize_embeddings=True)
    return ",".join(map(str, embedding.tolist()))

def find_similar_reviews(host: str, port: int, user: str, catalog: str, schema: str,
                        table: str, vector_str: str, top_k: int, embedding_column: str = "embedding",
                        http_scheme: str = 'http', principal_id: str = "", password: str = "",
                        disable_ssl_verification: bool = False) -> List[int]:
    """Execute vector search"""
    conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
    row_ids = []
    
    sql_query = f"""
    SELECT *
    FROM {catalog}.system.approx_nearest_neighbors(
        CAST(ARRAY[{vector_str}] AS array(real)),
        '{schema}.{table}.{embedding_column}',
        {top_k}
    )
    """
    
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        if results:
            row_ids = [row[0] for row in results]
    except Exception as e:
        st.error(f"Vector search failed: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn:
            conn.close()
    
    return row_ids

def get_review_details(host: str, port: int, user: str, catalog: str, schema: str,
                       table: str, row_ids: List[int], text_column: str = "comment",
                       http_scheme: str = 'http', principal_id: str = "", password: str = "",
                       disable_ssl_verification: bool = False) -> List[Tuple[int, str]]:
    """Retrieve review text for matched IDs"""
    conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
    results = []
    
    if row_ids:
        id_list_str = ", ".join(map(str, row_ids))
        sql_lookup = f"""
        SELECT row_id, {text_column}
        FROM {catalog}.{schema}.{table}
        WHERE row_id IN ({id_list_str})
        """
        
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(sql_lookup)
            raw_results = cursor.fetchall()
            
            # Create ordered map and preserve order
            comment_map = {row_id: comment for row_id, comment in raw_results}
            for row_id in row_ids:
                if row_id in comment_map:
                    results.append((row_id, comment_map[row_id]))
        except Exception as e:
            st.error(f"Lookup failed: {e}")
        finally:
            if cursor is not None:
                cursor.close()
            if conn:
                conn.close()
    
    return results

# Main Application
def main():
    st.markdown('<div class="main-header"> Similarity Search System</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header(" Configuration")
        
        # Presto Connection Settings
        st.subheader("Presto Connection")
        host = st.text_input("Host", value="", placeholder="e.g., x.x.x.x or localhost")
        port = st.number_input("Port", value=8080, min_value=1, max_value=65535)
        user = st.text_input("User", value="", placeholder="e.g., admin or your username")
        http_scheme = st.selectbox("HTTP Scheme", ["http", "https"], index=0)
        
        # SSL Verification is now always disabled (no toggle)
        disable_ssl_verification = True
        
        # Authentication settings
        use_auth = st.checkbox("Use Basic Authentication", value=False)
        if use_auth:
            password = st.text_input("Password", value="", type="password", help="Password for authentication")
        else:
            password = ""
        catalog = st.text_input("Catalog", value="", placeholder="e.g., iceberg")
        schema = st.text_input("Schema", value="", placeholder="e.g., my_schema or review_vectors")
        table = st.text_input("Table", value="", placeholder="e.g., reviews_embeddings")
        
        st.markdown("---")
        
        # Test Connection (moved above table configuration)
        if st.button(" Test Connection", use_container_width=True):
            try:
                conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
                results, _ = execute_query(conn, "SELECT 1", fetch=True)
                conn.close()
                if results:
                    st.success(" Connection successful!")
            except Exception as e:
                st.error(f" Connection failed: {e}")
        
        st.markdown("---")
        
        # Table Schema Configuration
        st.markdown("#### 📋 Table Schema Configuration")
        st.caption("Configure column names for the new table to be created")
        text_column = st.text_input("Text Column Name", value="", placeholder="e.g., comment or review_text", help="Column name for storing text/comments in the new table")
        embedding_column = st.text_input("Embedding Column Name", value="", placeholder="e.g., embedding or vector", help="Column name for storing vector embeddings in the new table")
        
        st.markdown("---")
        
        # Model Settings
        st.subheader("Model Settings")
        model_name = st.text_input(
            "Model Name",
            value="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load model button
        if st.button("🔄 Load Model", use_container_width=True):
            with st.spinner("Loading embedding model..."):
                st.session_state.model = load_embedding_model(model_name)
                if st.session_state.model:
                    st.success(f"✅ Model loaded successfully!")
                    st.info(f"Embedding dimension: {st.session_state.model.get_sentence_embedding_dimension()}")
    
    # Main Content Area - Tabs
    tab1, tab2, tab3, tab4 = st.tabs([" Data Ingestion"," Vector Search", " Tutorial", " About"])
    
    
    
    # TAB 1: Data Ingestion
    with tab1:
        st.markdown('<div class="sub-header">Data Ingestion Pipeline</div>', unsafe_allow_html=True)
        st.info(" This section allows you to ingest new data and create vector embeddings.")
        
        if st.session_state.model is None:
            st.warning(" Please load the embedding model from the sidebar first.")
        else:
            # File upload
            uploaded_file = st.file_uploader("Upload CSV file with reviews", type=['csv'])
            
            col1, col2 = st.columns(2)
            with col1:
                num_rows = st.number_input("Number of rows to process", min_value=1, value=100)
            with col2:
                batch_size = st.number_input("Batch size for insertion", min_value=1, max_value=100, value=20)
            
            s3_location = st.text_input("S3 Location", value=f"s3a://<bucketname>/{schema}")
            
            if uploaded_file is not None:
                st.success(f" File uploaded: {uploaded_file.name}")
                
                # Preview data and column selection
                df_preview = pd.read_csv(uploaded_file, nrows=5)
                
                if st.checkbox("Preview data"):
                    st.dataframe(df_preview)
                
                # Column selection for embedding generation
                st.markdown("#### 📋 Source Column Selection")
                st.caption("Select which column from your CSV to use for generating embeddings")
                available_columns = df_preview.columns.tolist()
                
                selected_column = st.selectbox(
                    "Select column for embedding generation:",
                    available_columns,
                    index=0 if available_columns else None,
                    help="Choose the column containing text data to generate vector embeddings from"
                )
                
                uploaded_file.seek(0)  # Reset file pointer
                
                if st.button(" Start Ingestion", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Load and process data
                        status_text.text("Step 1/5: Loading data...")
                        df: pd.DataFrame = pd.read_csv(uploaded_file, nrows=num_rows)
                        
                        # Use selected column for text generation
                        if not selected_column:
                            st.error("Please select a column for embedding generation.")
                            return
                        
                        # Filter to selected column and remove rows with NaN values
                        df = cast(pd.DataFrame, df[[selected_column]].dropna().reset_index(drop=True))
                        
                        # Use the selected column as text source
                        df[text_column] = df[selected_column].astype(str)
                        df['row_id'] = df.index + 1
                        df = cast(pd.DataFrame, df[['row_id', text_column]])
                        progress_bar.progress(20)
                        
                        # Step 2: Generate embeddings
                        status_text.text("Step 2/5: Generating embeddings...")
                        # Convert DataFrame column to list for encoding
                        text_list = cast(List[str], df[text_column].tolist())
                        # SentenceTransformer.encode accepts List[str] - type checker has incomplete stubs
                        embeddings = st.session_state.model.encode(  # type: ignore[arg-type,call-overload]
                            text_list,
                            show_progress_bar=False,
                            normalize_embeddings=True
                        )
                        df[embedding_column] = [emb.tolist() for emb in embeddings]
                        progress_bar.progress(40)
                        
                        # Step 3: Create schema
                        status_text.text("Step 3/5: Creating schema...")
                        conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
                        create_schema_sql = f"""
                        CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}
                        WITH (location = '{s3_location}')
                        """
                        execute_query(conn, create_schema_sql)
                        conn.close()
                        progress_bar.progress(50)
                        
                        # Step 4: Create table
                        status_text.text("Step 4/5: Creating table...")
                        conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
                        create_table_sql = f"""
                        CREATE TABLE IF NOT EXISTS {catalog}.{schema}.{table} (
                            row_id BIGINT,
                            {text_column} VARCHAR,
                            {embedding_column} ARRAY(REAL)
                        )
                        """
                        execute_query(conn, create_table_sql)
                        conn.close()
                        progress_bar.progress(60)
                        
                        # Step 5: Insert data
                        status_text.text("Step 5/5: Inserting data...")
                        conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
                        cursor = conn.cursor()
                        
                        batch = []
                        total_batches = (len(df) + batch_size - 1) // batch_size
                        processed_rows = 0
                        
                        # Use itertuples() instead of iterrows() for better performance
                        for row in df.itertuples(index=False, name='Row'):
                            row_id = row[0]  # row_id is first column
                            # Escape single quotes and handle potential SQL injection
                            comment = str(row[1]).replace("'", "''").replace("\\", "\\\\")  # text_column is second
                            embedding_array = "ARRAY[" + ",".join(map(str, row[2])) + "]"  # embedding_column is third
                            batch.append(f"({row_id}, '{comment}', CAST({embedding_array} AS ARRAY(REAL)))")
                            processed_rows += 1
                            
                            if len(batch) >= batch_size:
                                insert_sql = f"INSERT INTO {catalog}.{schema}.{table} (row_id, {text_column}, {embedding_column}) VALUES {', '.join(batch)}"
                                cursor.execute(insert_sql)
                                batch = []
                                progress = 60 + int(30 * processed_rows / len(df))
                                progress_bar.progress(progress)
                        
                        if batch:
                            insert_sql = f"INSERT INTO {catalog}.{schema}.{table} (row_id, {text_column}, {embedding_column}) VALUES {', '.join(batch)}"
                            cursor.execute(insert_sql)
                        
                        conn.commit()
                        cursor.close()
                        conn.close()
                        progress_bar.progress(90)
                        
                        # Step 6: Create vector index
                        status_text.text("Creating vector index...")
                        conn = get_presto_connection(host, port, user, catalog, schema, http_scheme, user, password, disable_ssl_verification)
                        cursor = conn.cursor()
                        index_cmd = f"CALL {catalog}.system.CREATE_VEC_INDEX('{catalog}.{schema}.{table}.{embedding_column}')"
                        cursor.execute(index_cmd)
                        conn.commit()
                        cursor.close()
                        conn.close()
                        
                        progress_bar.progress(100)
                        status_text.text(" Ingestion complete!")
                        st.success(f"Successfully ingested {len(df)} reviews with vector embeddings!")
                        st.session_state.ingestion_complete = True
                        
                    except Exception as e:
                        st.error(f" Ingestion failed: {e}")
                        progress_bar.empty()
                        status_text.empty()

    # TAB 2: Vector Search
    with tab2:
        st.markdown('<div class="sub-header">Semantic Search</div>', unsafe_allow_html=True)
        
        if st.session_state.model is None:
            st.warning(" Please load the embedding model from the sidebar first.")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                query_text = st.text_area(
                    "Enter your search query:",
                    placeholder="e.g., I love this product, it's amazing!",
                    height=100
                )
            
            with col2:
                top_k = st.slider("Number of results", min_value=1, max_value=50, value=10)
                search_button = st.button(" Search", use_container_width=True, type="primary")
            
            if search_button:
                if not query_text.strip():
                    st.warning("Please enter a search query.")
                else:
                    with st.spinner("Searching for similar reviews..."):
                        try:
                            # Generate embedding
                            start_time = time.time()
                            vector_str = embed_text(st.session_state.model, query_text)
                            
                            # Find similar reviews
                            row_ids = find_similar_reviews(
                                host, port, user, catalog, schema, table, vector_str, top_k, embedding_column,
                                http_scheme, user, password, disable_ssl_verification
                            )
                            
                            # Get review details
                            if row_ids:
                                results = get_review_details(
                                    host, port, user, catalog, schema, table, row_ids, text_column,
                                    http_scheme, user, password, disable_ssl_verification
                                )
                                elapsed = time.time() - start_time
                                
                                st.session_state.search_results = results
                                
                                st.markdown(f'<div class="success-box"> Found {len(results)} similar reviews in {elapsed:.3f}s</div>', 
                                          unsafe_allow_html=True)
                            else:
                                st.warning("No matching reviews found.")
                                st.session_state.search_results = []
                        
                        except Exception as e:
                            st.error(f"Search failed: {e}")
            
            # Display Results
            if st.session_state.search_results:
                st.markdown("---")
                st.markdown('<div class="sub-header">Search Results</div>', unsafe_allow_html=True)
                
                # Export button
                col1, col2, col3 = st.columns([1, 1, 4])
                with col1:
                    # Prepare CSV data
                    csv_data = "Row ID,Review\n"
                    for row_id, comment in st.session_state.search_results:
                        csv_data += f'{row_id},"{comment.replace(chr(34), chr(34)+chr(34))}"\n'
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="search_results.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Prepare JSON data
                    json_data = json.dumps([
                        {"row_id": row_id, "review": comment}
                        for row_id, comment in st.session_state.search_results
                    ], indent=2)
                    
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name="search_results.json",
                        mime="application/json"
                    )
                
                st.markdown("---")
                
                # Display each result
                for idx, (row_id, comment) in enumerate(st.session_state.search_results, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <strong>#{idx} - Row ID: {row_id}</strong><br>
                            {comment}
                        </div>
                        """, unsafe_allow_html=True)
    # TAB 3: Tutorial
    with tab3:
        st.markdown('<div class="sub-header">🎓 Getting Started Tutorial</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Welcome to watsonx.data Similarity Search!
        
        This tutorial will guide you through using the application step by step.
        """)
        
        # Tutorial Steps
        with st.expander("📋 Step 1: Configure Connection Settings", expanded=True):
            st.markdown("""
            **In the sidebar, configure your Presto connection:**
            
            1. **Host**: Enter your Presto engine hostname or IP address
            2. **Port**: 
                | Environment | Port |
                | :--- | :--- |
                | **localhost** | 8080 |
                | **CPD** | 443 |
                | **SaaS** | xxxxx | 
            3. **User**: Your username for Presto connection
            4. **HTTP Scheme**: Select 'http' or 'https' based on your server configuration
            5. **Basic Authentication** (Optional):
               - Check "Use Basic Authentication" if your server requires it
               - Enter your password when prompted
            6. **Catalog**: Set to 'iceberg' for watsonx.data
            7. **Schema**: Choose or create a schema name (e.g., 'my_vectors')
            8. **Table**: Name for your table (e.g., 'product_reviews')
            
            💡 **Tip**: Click " Test Connection" to verify your settings work!
            """)
        
        with st.expander("🏗️ Step 2: Configure Table Schema"):
            st.markdown("""
            **Set up your table column names:**
            
            1. **Text Column Name**: What to call the text column in your table 
               - This will store the actual text/review content
               - Choose a meaningful name for your use case
            2. **Embedding Column Name**: What to call the vector column
               - This will store the AI-generated vector embeddings
               - Must be an ARRAY(REAL) type column
            
            ❗ **Note**: These names will be used when creating your new table in watsonx.data. Make sure they follow SQL naming conventions (no spaces, special characters).
            """)
        
        with st.expander("🤖 Step 3: Load the AI Model"):
            st.markdown("""
            **Load the embedding model:**
            
            1. The default model 'sentence-transformers/all-MiniLM-L6-v2' works well for most text
            2. Click "🔄 Load Model" and wait for it to download and load
            3. You'll see a success message with the embedding dimension
            
            💡 **Tip**: This step is required before you can ingest data or search!
            """)
        
        with st.expander("📥 Step 4: Ingest Your Data"):
            st.markdown("""
            **Upload and process your CSV file:**
            
            1. Go to the "📥 Data Ingestion" tab
            2. Upload a CSV file with text data (any CSV with text columns)
            3. **Preview your data** (optional checkbox):
               - View the first 5 rows of your CSV
               - See all available columns
            4. **Select Source Column** (Important!):
               - Choose which column from your CSV contains the text for embedding generation
               - This can be reviews, comments, descriptions, or any text field
               - The selected column will be used to generate vector embeddings
            5. **Configure processing settings**:
               - **Number of rows**: How many rows to process (start small for testing)
               - **Batch size**: Rows per insert batch (20 is recommended)
            6. **Set S3 location**: Storage path for your Iceberg table data
            7. Click "🚀 Start Ingestion"
            
            **The system will automatically:**
            - Load your data from the selected column
            - Remove any rows with missing/null values
            - Generate vector embeddings using AI
            - Create the schema and table (if they don't exist)
            - Insert data with embeddings in batches
            - Create a vector index for fast search
            
            💡 **Tip**: Start with 100-1000 rows for testing! You can always ingest more data later.
            """)
        
        with st.expander("🔍 Step 5: Search Your Data"):
            st.markdown("""
            **Perform semantic searches:**
            
            1. Go to the "🔍 Similarity Search" tab
            2. Enter a natural language query (e.g., "I love this product")
            3. Adjust the number of results you want
            4. Click "🔍 Search"
            5. View results ranked by similarity
            6. Download results as CSV or JSON if needed
            
            💡 **Tip**: Try different phrasings - semantic search understands meaning, not just keywords!
            """)
        
        with st.expander("❓ Common Issues & Solutions"):
            st.markdown("""
            **Connection Problems:**
            - Verify host, port, and credentials are correct
            - Check network connectivity to watsonx.data
            - For authentication errors, verify username and password
            - Ensure the catalog and schema exist or can be created
            
            **Authentication Problems:**
            - Enable "Use Basic Authentication" if your server requires it
            - Verify your password is correct
            - Check if your user has proper permissions
            
            **Model Loading Issues:**
            - Check internet connection for first-time model download
            - Wait for the model to fully load before proceeding (can take 1-2 minutes)
            - Try refreshing the page if it gets stuck
            - Clear browser cache if problems persist
            
            **Data Ingestion Problems:**
            - Ensure CSV file is properly formatted (valid CSV structure)
            - **Important**: Select the correct source column containing text data
            - Check that selected column has actual text content (not empty/null)
            - Verify S3 location permissions and bucket access
            - Start with smaller datasets (100-500 rows) for testing
            - If batch insertion fails, try reducing the batch size
            
            **Column Selection Issues:**
            - Make sure you select a column that contains text data
            - Avoid columns with mostly null/empty values
            - Numeric or date columns won't work well for embeddings
            
            **Search Not Working:**
            - Make sure data ingestion completed successfully (100% progress)
            - Verify the model is loaded (check for success message)
            - Check that the table and vector index were created
            - Ensure you're searching in the correct schema and table
            - Try a different search query with more descriptive text
            """)
        
        st.markdown("---")
        st.info("💡 **Pro Tip**: Follow the steps in order for the best experience. Each step builds on the previous one!")


if __name__ == "__main__":
    main()