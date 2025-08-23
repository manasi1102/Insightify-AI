## Insightify – AI Knowledge Assistant
> This project simulates how companies can turn unstructured internal documents into searchable insights using a Retrieval-Augmented Generation (RAG) pipeline. It’s designed for real-world enterprise documents—emails, feedback, reports—not just open web content.
 
## Project Overview
Most companies generate a flood of internal documentation—weekly reports, emails, user feedback, transcripts—but that information is rarely easy to access, summarize, or analyze. Insightify is a working demo that shows how LLMs can help with that.

We built it to:

* Convert unstructured internal content into structured JSONL format.
* Embed and index the content for fast semantic retrieval.
* Run natural language queries against it using a local LLM pipeline.
* Return answers grounded in actual internal context — not generic web data.
 
## Authors
* Hema Manasi Potnuru
* Mahimna Darji
 
## Tech Stack
| Layer        | Tools Used                       |
| ------------ | -------------------------------- |
| Pre-processing |Python, PyMuPDF, pdfplumber, jsonlines                    |
| Embeddings      | Hugging Face BAAI/bge-base-en-v1.5, Sentence Transformers |
| Indexing   | FAISS               |
| Retrieval   | Semantic similarity search with FAISS                           |
| Generation  | Hugging Face Transformers (google/flan-t5-base, google/flan-t5-large)   |
| Dev Tools   | VSCode, Anaconda, Git, Jupyter Notebook               |
 
## Features Built
### Document Parsing & Structuring
* Cleaned and structured documents from multiple formats (PDFs, TXT etc.)
* Extracted relevant fields like title, highlights, date, and follow-ups
### Smart Chunking + Embedding
* Used LangChain’s RecursiveCharacterTextSplitter for hierarchical chunking
* Generated embeddings with bge-base-en-v1.5 for semantically rich vectors
### FAISS Vector Index
* Built and stored a dense vector index with chunk-level metadata
* Supported fast and accurate retrieval for QA and document summarization
### Retrieval-Augmented QA
* Natural language interface for querying internal docs
* Generated answers using fine-tuned T5 models from Hugging Face
 
## What Makes It Stand Out
### End-to-End RAG Pipeline
* Covers everything from document ingestion, smart chunking, embeddings, and similarity search to generating clear answers with a language model.
* No shortcuts — everything is done right for practical use.
### Works with Real Business Documents
* Uses real company emails, weekly reports, feedback notes, and meeting transcripts — no web/ Wikipedia text.
### Multi-Format, Contextual Intelligence
* Understands PDFs, emails, notes, transcripts — so you can ask detailed questions across all your business documents.
### Answers That Feel Human and Reliable
* Results are clear and based directly on company data, not generic or vague answers.
### Ideal for Real-World Use
* Great for internal assistants or knowledgebases in Indian mid-size to large companies — helps teams quickly find and act on important insights.
### Solid, Scalable Stack
* Handles large document collections, preserves metadata, and retrieves information fast without experimental or fragile features.
 
## Future Enhancements
* Add Streamlit or web-based UI for query interface
* Support longer context windows using more advanced models
* Implement chunk summarization and ranking
* Build QA evaluation harness to benchmark answer quality
 
