import time
import json
import sys
from pathlib import Path
try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai library not installed. Run 'pip install openai'")
    sys.exit(1)

# --- Configuration ---
LLAMA_SERVER_URL = "http://localhost:8080/v1"
VECTOR_STORE_MOCK = [
    {"id": 1, "text": "TTFT stands for Time To First Token. It measures the latency of the prefill stage.", "source": "Lesson 0"},
    {"id": 2, "text": "TPOT stands for Time Per Output Token. It measures the latency of the decode stage.", "source": "Lesson 0"},
    {"id": 3, "text": "Continuous batching allows new requests to join the batch while others are still generating.", "source": "Lesson 3"},
    {"id": 4, "text": "Quantization reduces the precision of model weights to save RAM and increase speed.", "source": "Lesson 1"},
]

client = OpenAI(base_url=LLAMA_SERVER_URL, api_key="sk-no-key-required")

def retrieve(query: str, k: int = 2) -> list[dict]:
    """
    Mock retrieval function. In a real scenario, this would call 
    a vector database like ChromaDB, Qdrant, or Pinecone (N19).
    """
    print(f"   [Retrieve] Searching for: '{query}'")
    # Simple keyword match for demonstration
    keywords = query.lower().split()
    results = []
    for doc in VECTOR_STORE_MOCK:
        if any(kw in doc["text"].lower() for kw in keywords):
            results.append(doc)
    
    # Return top-K (or all if matches are fewer)
    return results[:k] if results else VECTOR_STORE_MOCK[:k]

def build_prompt(query: str, contexts: list[dict]) -> list[dict]:
    """
    Constructs an OpenAI-style message list (System + Context + User).
    """
    context_text = "\n".join([f"- {c['text']} (Source: {c['source']})" for c in contexts])
    
    system_prompt = (
        "You are a helpful AI assistant for the Model Serving Lab. "
        "Use the provided context to answer the user's question accurately. "
        "If the answer isn't in the context, say you don't know."
    )
    
    user_content = (
        f"Context information is below:\n"
        f"---------------------\n"
        f"{context_text}\n"
        f"---------------------\n"
        f"Query: {query}\n"
        f"Answer:"
    )
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

def answer(query: str) -> str:
    """
    Ties retrieval, prompt building, and LLM call together.
    """
    t0 = time.perf_counter()
    
    # 1. Retrieve
    contexts = retrieve(query)
    
    # 2. Build Prompt
    messages = build_prompt(query, contexts)
    
    # 3. Call LLM
    print(f"   [LLM] Calling llama-server...")
    try:
        response = client.chat.completions.create(
            model="local-model", # llama-server ignores this and uses the loaded model
            messages=messages,
            temperature=0.0, # Greedy for benchmark consistency
            max_tokens=150
        )
        ans = response.choices[0].message.content
    except Exception as e:
        return f"Error calling server: {e}"
    
    t_total = (time.perf_counter() - t0) * 1000.0
    print(f"   [Done] Total latency: {t_total:.1f}ms")
    
    print("\n--- Sources ---")
    for c in contexts:
        print(f" * {c['source']}: {c['text'][:50]}...")
    
    return ans

if __name__ == "__main__":
    queries = [
        "What is TTFT?",
        "Explain quantization.",
        "How does continuous batching work?"
    ]
    
    print("=== Milestone 1 Integration Pipeline ===\n")
    for q in queries:
        print(f"\nQUERY: {q}")
        result = answer(q)
        print(f"\nANSWER:\n{result}")
        print("-" * 50)
