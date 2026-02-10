import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
CHUNKS_PATH = "data/processed/chunks.json"
EMBEDDINGS_DIR = "data/processed/embeddings"
BATCH_SIZE = 100
MAX_CHARS = 20000


def truncate_text(text, max_chars=MAX_CHARS):
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def generate_embeddings():
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    total = len(chunks)
    print(f"Total chunks: {total}")
    print(f"Using model: {EMBEDDING_MODEL}")

    existing = [f for f in os.listdir(EMBEDDINGS_DIR) if f.startswith("batch_") and f.endswith(".npy")]
    start_batch = len(existing)
    start_idx = start_batch * BATCH_SIZE

    if start_idx > 0:
        print(f"Resuming from chunk {start_idx} (batch {start_batch})...")

    for i in range(start_idx, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [truncate_text(chunk["text"]) for chunk in batch]

        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
            )

            embeddings = [e.embedding for e in response.data]
            arr = np.array(embeddings, dtype="float32")

            batch_num = i // BATCH_SIZE
            np.save(os.path.join(EMBEDDINGS_DIR, f"batch_{batch_num:05d}.npy"), arr)

            print(f"  Embedded {min(i + BATCH_SIZE, total)}/{total}")

        except Exception as e:
            print(f"  Error at chunk {i}: {e}")
            print(f"  Re-run to resume from chunk {i}.")
            return

    print("Combining batches...")
    all_files = sorted([f for f in os.listdir(EMBEDDINGS_DIR) if f.startswith("batch_")])
    all_embeddings = np.concatenate([np.load(os.path.join(EMBEDDINGS_DIR, f)) for f in all_files])
    np.save(os.path.join("data/processed", "embeddings.npy"), all_embeddings)

    print(f"\nDone! Shape: {all_embeddings.shape}")
    print(f"Saved to data/processed/embeddings.npy")


if __name__ == "__main__":
    generate_embeddings()
