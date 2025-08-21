import json
import pickle
import os
from pathlib import Path
from tqdm import tqdm

from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss

# -----------------------------
# 1. Load All JSONL Documents
# -----------------------------
def load_all_jsonl(folder_path):
    all_docs = []
    for file in Path(folder_path).glob("*.jsonl"):
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if "title" in data and "text" in data:
                    all_docs.append({
                        "title": data["title"],
                        "text": data["text"]
                    })
    return all_docs

# -----------------------------
# 2. Chunk Documents
# -----------------------------
def chunk_documents(docs, chunk_size=600, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = []
    for doc in docs:
        split_texts = splitter.split_text(doc["text"])
        for chunk in split_texts:
            chunks.append({
                "title": doc["title"],
                "text": chunk.strip()
            })
    return chunks

# -----------------------------
# 3. Embed & Store with FAISS
# -----------------------------
def build_vector_store(chunks, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    print("Loading embedding model...")
    model = SentenceTransformer(model_name)

    print(f"Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print("Creating FAISS index...")
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print("Saving index to faiss_index.index and metadata to chunk_metadata.pkl...")
    faiss.write_index(index, "faiss_index.index")

    # Save metadata with title and text
    with open("chunk_metadata.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Vector store creation complete!")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    print("Loading documents...")
    documents = load_all_jsonl("jsonl_files")  # <-- make sure your folder is named correctly
    chunks = chunk_documents(documents)
    build_vector_store(chunks)
