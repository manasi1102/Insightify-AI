import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from rich import print
from rich.console import Console

# ------------------- Config -------------------
INDEX_PATH = "faiss_index.index"
METADATA_PATH = "chunk_metadata.pkl"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "google/flan-t5-base"
TOP_K = 5
MAX_INPUT_TOKENS = 512
MAX_OUTPUT_TOKENS = 150

# ------------------- Setup -------------------
console = Console()

def load_vector_store():
    index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def load_models():
    console.print("[bold]Loading embedding model...[/bold]")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    console.print("[bold]Loading generation model...[/bold]")
    tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(GENERATION_MODEL_NAME).to(torch.device("cpu"))  # Use CPU for stability

    return embedding_model, tokenizer, model

def retrieve_chunks(query, embedding_model, index, metadata):
    query_embedding = embedding_model.encode([query])
    scores, indices = index.search(np.array(query_embedding).astype("float32"), TOP_K)

    retrieved = []
    for idx in indices[0]:
        meta = metadata[idx]
        retrieved.append({
            "title": meta.get("title", "[No title]"),
            "text": meta.get("text", "[no content]")[:200].replace("\n", " ").strip() + "..."  # trim snippet
        })
    return retrieved

def build_prompt(query, chunks):
    context = "\n\n".join(f"{i+1}. {chunk['text']}" for i, chunk in enumerate(chunks))
    prompt = f"""You are an analyst assistant summarizing product feedback.

Question: {query}

Context:
{context}

Instructions: Answer the question based on the above context. Be specific and mention examples when available."""
    return prompt

def generate_answer(prompt, tokenizer, model):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_TOKENS).to(torch.device("cpu"))
    outputs = model.generate(
        **inputs,
        max_new_tokens=MAX_OUTPUT_TOKENS,
        do_sample=False,
        num_beams=4
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def run_rag_pipeline(query):
    index, metadata = load_vector_store()
    embedding_model, tokenizer, model = load_models()

    console.print(f"\n[bold]Query:[/bold] {query}\n")
    chunks = retrieve_chunks(query, embedding_model, index, metadata)

    console.print("[bold]Retrieved Chunks:[/bold]")
    for i, chunk in enumerate(chunks):
        console.print(f"• Chunk {i+1}: Title: {chunk['title']} | Snippet: {chunk['text']}")

    prompt = build_prompt(query, chunks)

    console.print("\n[bold]Generating answer...[/bold]\n")
    answer = generate_answer(prompt, tokenizer, model)
    return answer

# ------------------- Run -------------------
if __name__ == "__main__":
    query = input("\nEnter your question: ").strip()
    answer = run_rag_pipeline(query)
    print(f"\n[bold green]Answer:[/bold green] {answer}")
