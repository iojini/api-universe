import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
CHUNKS_PATH = "data/processed/chunks.json"
OUTPUT_PATH = "data/processed/chunks_with_embeddings.json"
BATCH_SIZE = 100


def generate_embeddings():
    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    print(f"Generating embeddings for {len(chunks)} chunks...")
    print(f"Using model: {EMBEDDING_MODEL}")

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [chunk["text"] for chunk in batch]

        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )

        for j, embedding_data in enumerate(response.data):
            chunks[i + j]["embedding"] = embedding_data.embedding

        print(f"  Embedded {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(chunks, f)

    print(f"\nDone! Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_embeddings()