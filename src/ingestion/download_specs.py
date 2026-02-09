import os
import json
import httpx

APIS_GURU_LIST = "https://api.apis.guru/v2/list.json"
RAW_DIR = "data/raw"


def download_specs(limit=100):
    os.makedirs(RAW_DIR, exist_ok=True)

    print("Fetching API list from APIs.guru...")
    response = httpx.get(APIS_GURU_LIST, timeout=30)
    apis = response.json()

    count = 0
    for name, info in apis.items():
        if count >= limit:
            break

        try:
            preferred = info.get("preferred", "")
            version_info = info["versions"].get(preferred, {})
            spec_url = version_info.get("swaggerUrl") or version_info.get("openapiVer")

            if not spec_url:
                first_version = list(info["versions"].values())[0]
                spec_url = first_version.get("swaggerUrl", "")

            if not spec_url:
                continue

            print(f"[{count + 1}/{limit}] Downloading: {name}")
            spec_response = httpx.get(spec_url, timeout=15, follow_redirects=True)
            spec_data = spec_response.text

            safe_name = name.replace(":", "_").replace("/", "_")
            filepath = os.path.join(RAW_DIR, f"{safe_name}.json")

            with open(filepath, "w") as f:
                f.write(spec_data)

            count += 1

        except Exception as e:
            print(f"  Skipping {name}: {e}")

    print(f"\nDone! Downloaded {count} API specs to {RAW_DIR}/")


if __name__ == "__main__":
    download_specs(limit=100)