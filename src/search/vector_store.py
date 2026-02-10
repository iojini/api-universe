import os
import json
import numpy as np
import faiss

EMBEDDINGS_PATH = "data/processed/embeddings.npy"
CHUNKS_PATH = "data/processed/chunks.json"
INDEX_PATH = "data/processed/faiss_index.bin"
METADATA_PATH = "data/processed/metadata.json"


def build_index():
    embeddings = np.load(EMBEDDINGS_PATH)
    print(f"Loaded embeddings: {embeddings.shape}")

    with open(CHUNKS_PATH, "r") as f:
        chunks = json.load(f)

    count = min(len(chunks), embeddings.shape[0])
    embeddings = embeddings[:count]
    chunks = chunks[:count]

    print(f"Building FAISS index from {count} vectors...")

    dimension = embeddings.shape[1]
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    metadata = []
    for c in chunks:
        entry = {k: v for k, v in c.items() if k != "embedding"}
        metadata.append(entry)

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f)

    print(f"Done! Index saved to {INDEX_PATH}")
    print(f"Metadata saved to {METADATA_PATH}")
    print(f"Dimension: {dimension}, Vectors: {index.ntotal}")


if __name__ == "__main__":
    build_index()
