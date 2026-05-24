# RAG-Project

A Streamlit-based Retrieval-Augmented Generation (RAG) application for document intelligence.

This project ingests PDF documents, creates a Chroma vector store from text chunks, and lets users ask questions against the uploaded documents using a Groq-powered LLM.

## Key features

- PDF document ingestion via `data/` folder or upload
- Text splitting and embedding using `sentence-transformers/all-MiniLM-L6-v2`
- Chroma vector store persistence
- Streamlit UI for interactive question answering
- Docker support for containerized deployment

## Repository structure

- `app/`
  - `streamlit_app.py` - main Streamlit application
  - `functions.py` - document loading, vector store creation, embedding and retrieval logic
  - `requirements.txt` - Python dependencies for the Streamlit app
  - `dockerfile` - container definition for production deployment
  - `.streamlit/config.toml` - Streamlit UI and server settings
- `data/` - PDF source files for processing
- `vectorstore_chroma/` - generated Chroma vector store (should not be committed)
- `myenv/` - local Python virtual environment (ignored)
- `.gitignore` - configured ignore rules for generated, secret, and environment files

## Setup

### 1. Clone repository

```bash
git clone https://github.com/rushikeshc7/RAG-Project.git
cd RAGLLMs
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r app/requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the repository root with the following values:

```text
GROQ_API_KEY=your_groq_api_key
HUGGING_FACE_API_KEY=your_huggingface_api_key
```

> Do not commit `.env` or secrets to GitHub.

### 5. Run the app

```bash
streamlit run app/streamlit_app.py
```

Then open the local URL shown in the terminal.

## Data

- Place PDF files in the `data/` directory.
- The notebook and Streamlit app load documents from `data/*.pdf`.
- Example files are already included in the `data/` folder.

## Notes on generated files

The repository ignores the following generated or local-only folders:

- `app/db/`
- `vectorstore_chroma/`
- `myenv/`
- `.env`
- `*.ipynb`

If you want to track notebooks or sample data, remove the appropriate ignore rules, but do not commit large generated vector stores or secrets.

## Deployment

### Docker

Build the container:

```bash
docker build -t rag-project .
```

Run it locally:

```bash
docker run -p 8501:8501 rag-project
```

### Streamlit Community Cloud

This app can also be deployed on Streamlit Community Cloud by connecting the GitHub repository and using `app/streamlit_app.py` as the entrypoint.

## Troubleshooting

- If push fails due to permissions, ensure you are authenticated with the GitHub account that has write access.
- If the app does not start, verify that `GROQ_API_KEY` is set and that dependencies are installed.
- If `data/*.pdf` is empty, add PDF files to the `data/` folder before running.

## License

This project does not include a license file. Add one if you want to define reuse terms.
