import os
import json
import numpy as np
import faiss

EMBEDDINGS_PATH = "data/processed/chunks_with_embeddings.json"
INDEX_PATH = "data/processed/faiss_index.bin"
METADATA_PATH = "data/processed/metadata.json"


def build_index():
    with open(EMBEDDINGS_PATH, "r") as f:
        chunks = json.load(f)

    print(f"Building FAISS index from {len(chunks)} chunks...")

    embeddings = np.array([c["embedding"] for c in chunks], dtype="float32")
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    faiss.normalize_L2(embeddings)
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