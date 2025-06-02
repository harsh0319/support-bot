
# RAG-Based Complaint Handling System

This project sets up a Retrieval-Augmented Generation (RAG) pipeline using Qdrant, FastAPI, OpenAI, and Streamlit for storing and querying complaint data.

---

## 🚀 Getting Started

### 1. Create `.env` File

Create a `.env` file in the project root directory and add the necessary environment variables:

- `qdrant_url`
- `qdrant_key`
- `OPENAI_API_KEY`
- `FASTAPI_BASE_URL`
- `MONGODB_URL`
- `DATABASE_NAME`

> ⚠️ Keep your `.env` file private and do not expose it in public repositories.

---

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Store Data in Vector Database

Run the following script to populate the Qdrant vector database:

```bash
python data_store.py
```

---

### 5. Start FastAPI Backend

Launch the FastAPI server:

```bash
uvicorn main:app --reload
```

---

### 6. Run Streamlit App

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

---

## 📁 Project Structure

```
.
├── data_store.py
├── main.py
├── streamlit_app.py
├── requirements.txt
├── .env               # Not included in version control
```

---

## ✅ Tech Stack

- Qdrant (Vector Database)
- FastAPI (Backend API)
- OpenAI (LLM Integration)
- Streamlit (Frontend UI)
- MongoDB (Database)

---

## 🔒 Security Note

Ensure `.env` and any credentials remain secure and are not exposed in public repositories.
