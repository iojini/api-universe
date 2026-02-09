import os
import json
import yaml


def extract_api_info(spec):
    """Pull key fields from an OpenAPI/Swagger spec."""
    info = spec.get("info", {})
    return {
        "title": info.get("title", "Unknown API"),
        "description": info.get("description", ""),
        "version": info.get("version", ""),
        "base_url": spec.get("servers", [{}])[0].get("url", "")
            if spec.get("servers")
            else spec.get("host", ""),
    }


def extract_endpoints(spec):
    """Extract each endpoint as a separate chunk."""
    paths = spec.get("paths", {})
    endpoints = []

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, details in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "parameters": [
                        p.get("name", "") for p in details.get("parameters", [])
                    ],
                    "tags": details.get("tags", []),
                })

    return endpoints


def chunk_spec(filepath):
    """Turn one API spec file into searchable chunks."""
    with open(filepath, "r") as f:
        content = f.read()

    try:
        spec = json.loads(content)
    except json.JSONDecodeError:
        try:
            spec = yaml.safe_load(content)
        except Exception:
            return []

    if not isinstance(spec, dict):
        return []

    api_info = extract_api_info(spec)
    endpoints = extract_endpoints(spec)
    chunks = []

    # Chunk 1: API overview
    overview_text = f"{api_info['title']}\n{api_info['description']}"
    if overview_text.strip():
        chunks.append({
            "text": overview_text,
            "metadata": {
                "type": "overview",
                "api_name": api_info["title"],
                "version": api_info["version"],
                "base_url": api_info["base_url"],
                "source_file": os.path.basename(filepath),
            },
        })

    # Chunk 2+: Each endpoint
    for ep in endpoints:
        ep_text = (
            f"{ep['method']} {ep['path']}\n"
            f"{ep['summary']}\n"
            f"{ep['description']}"
        ).strip()

        if ep_text:
            chunks.append({
                "text": ep_text,
                "metadata": {
                    "type": "endpoint",
                    "api_name": api_info["title"],
                    "method": ep["method"],
                    "path": ep["path"],
                    "tags": ep["tags"],
                    "parameters": ep["parameters"],
                    "source_file": os.path.basename(filepath),
                },
            })

    return chunks


def chunk_all_specs(raw_dir="data/raw", output_path="data/processed/chunks.json"):
    """Process all specs and save chunks."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    all_chunks = []

    files = [f for f in os.listdir(raw_dir) if f.endswith(".json")]
    print(f"Processing {len(files)} spec files...")

    for i, filename in enumerate(files):
        filepath = os.path.join(raw_dir, filename)
        chunks = chunk_spec(filepath)
        all_chunks.extend(chunks)
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(files)} files ({len(all_chunks)} chunks so far)")

    with open(output_path, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\nDone! Created {len(all_chunks)} chunks saved to {output_path}")
    return all_chunks


if __name__ == "__main__":
    chunk_all_specs()