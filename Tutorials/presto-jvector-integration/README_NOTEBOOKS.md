# Presto JVector Integration - Jupyter Notebooks

This directory contains Jupyter notebooks demonstrating vector similarity search using Presto/Iceberg with JVector integration.


## 🚀 Quick Start

### Prerequisites

1. **Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Register the Environment as a Kernel**
   ```bash
   python -m ipykernel install --user --name=presto-jvector-env --display-name "Presto JVector (Venv)"
   ```

4. **Required Files**
   - Have a csv test sample data file (eg. "test/amazon_reviews.csv" with column "reviewText")

5. **Presto/watsonx.data Setup**
   - Presto server should be up and running
   - Iceberg catalog configured
   - S3 bucket associated with the catalog

### Running the Notebooks

1. **Start Jupyter**
   ```bash
   jupyter notebook
   ```

2. **Run Notebooks in Order**
   - First: `01_Vector_Index_Creation.ipynb` - To create and populate the table
   - Then: `02_Similarity_Search.ipynb` - To perform similarity searches

---

## ⚙️ Configuration

Both notebooks use similar configuration parameters. Update these at the top of each notebook:

### Connection Settings

```python
# Presto Connection
HOST = ''                       # Your Presto host address
PORT = 8080                     # Port: 443 for CPD, check UI for SaaS
USER = ''                       # Your username
HTTP_SCHEME = 'http'            # 'http' or 'https'

# Authentication (Optional)
PRINCIPAL_ID = ''               # Leave empty if not using auth
PASSWORD = ''                   # Leave empty if not using auth
DISABLE_SSL_VERIFICATION = True # Set True for self-signed certs

# Database Configuration
CATALOG = 'catalog_name'        # The catalog your bucket is associated with
SCHEMA = 'schema_name'          # Your schema name
TABLE = 'table_name'            # Your table name
```

### Connection Parameters Explained

- **HOST**: The host address of your Presto server
- **PORT**: 
  - For **CPD (Cloud Pak for Data)**: Use port **443**
  - For **SaaS**: Get the port from the watsonx.data UI
  - For local/development: Usually **8080**
- **CATALOG**: The catalog your bucket is associated with in watsonx.data
- **SCHEMA**: Your database schema name
- **TABLE**: The table name for storing embeddings

### Data Processing Settings (01_Vector_Index_Creation.ipynb)

Example

```python
# Data Configuration
CSV_FILE = "*.csv"
SOURCE_COLUMN = ' Column Text'   # Column to embed from your CSV
TEXT_COLUMN = ''                 # Column name in the table
EMBEDDING_COLUMN = ''            # Column name for vectors
NUM_ROWS = 100                   # Number of rows to process
BATCH_SIZE = 20                  # Batch size for inserts
```

### Search Settings (02_Similarity_Search.ipynb)

```python
# Search Configuration
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
TOP_K = 10                             # Number of similar results to return
INPUT_TEXT = "Your search query here"  # Modify this to search
```

---

## 📊 Notebook Workflow

### Notebook 1: Data Ingestion

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Configuration & Setup                                    │
│    - Set connection parameters                              │
│    - Import required libraries                              │
│    - Define helper functions                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Test Connection                                          │
│    - Verify Presto connectivity                             │
│    - Validate catalog and schema access                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Generate Embeddings                                      │
│    - Load CSV data                                          │
│    - Load Sentence Transformer model                        │
│    - Generate 384-dimensional vectors                       │
│    - Save embeddings to CSV                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Create Schema                                            │
│    - Create Iceberg schema if not exists                    │
│    - Set S3 location                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Create Table                                             │
│    - Define table schema (row_id, text, embedding)          │
│    - Create Iceberg table                                   │
│    - Validate table structure                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. Insert Data                                              │
│    - Generate batch INSERT statements                       │
│    - Execute inserts in batches                             │
│    - Verify row count                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Create Vector Index                                      │
│    - Create JVector index on embedding column               │
│    - Enable fast similarity search                          │
└─────────────────────────────────────────────────────────────┘
```

### Notebook 2: Vector Search

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Setup & Configuration                                     │
│    - Set connection parameters                               │
│    - Load embedding model                                    │
│    - Define search functions                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Input & Embed                                             │
│    - Define search query text                                │
│    - Generate query embedding                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Vector Search                                             │
│    - Execute approx_nearest_neighbors query                  │
│    - Get TOP_K matching row IDs                              │
│    - Measure search time                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Retrieve & Display Results                                │
│    - Fetch review text for matched IDs                       │
│    - Display results in order of similarity                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Key Features

### Vector Embeddings
- Uses **Sentence Transformers** (all-MiniLM-L6-v2 model)
- Generates **384-dimensional** vectors
- Normalized embeddings for cosine similarity

### Batch Processing
- Configurable batch size (default: 20 rows)
- Efficient bulk inserts
- Progress tracking

### Vector Index
- JVector integration for fast similarity search
- Approximate nearest neighbor search
- Sub-second query times

### Flexible Configuration
- Customizable column names
- Configurable source data column
- Adjustable number of results (TOP_K)

---

## 💡 Usage Examples

### Example 1: Positive Reviews
```python
INPUT_TEXT = "I love this product, it's amazing!"
```
**Expected Results:** Reviews with positive sentiment and similar expressions

### Example 2: Negative Reviews
```python
INPUT_TEXT = "Poor quality and disappointing"
```
**Expected Results:** Reviews with negative sentiment

### Example 3: Specific Features
```python
INPUT_TEXT = "Comfortable and fits perfectly"
```
**Expected Results:** Reviews mentioning comfort and fit

---

## 🔧 Troubleshooting

### Environment Setup Issues

#### Kernel Selection in IDEs

**Problem:** Your IDE (VS Code, PyCharm, JupyterLab) asks you to select a kernel when opening the notebooks.

**Solution:**

1. **Create a Virtual Environment** (if not already done):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Jupyter Kernel**:
   ```bash
   pip install ipykernel
   python -m ipykernel install --user --name=presto-jvector --display-name "Python (Presto JVector)"
   ```

4. **Select the Kernel in Your IDE**:
   - **VS Code**: Click on the kernel selector in the top-right corner → Select "Python (Presto JVector)"
   - **JupyterLab**: Kernel → Change Kernel → Select "Python (Presto JVector)"
   - **PyCharm**: Run → Edit Configurations → Select the virtual environment interpreter

#### Common Kernel Issues

**Issue: "No kernel found" or "Kernel not starting"**

**Solutions:**
- Ensure Jupyter is installed in your virtual environment:
  ```bash
  pip install jupyter notebook ipykernel
  ```
- Restart your IDE after installing the kernel
- Check that the virtual environment is activated before launching the IDE

**Issue: "Module not found" errors when running cells**

**Solutions:**
- Verify you're using the correct kernel (check top-right corner)
- Reinstall dependencies in the active environment:
  ```bash
  pip install -r requirements.txt
  ```
- Restart the kernel: Kernel → Restart Kernel
