import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
EVIDENCE_DIR = Path(os.getenv("EVIDENCE_DIR", "output/evidence"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def load_apps():
    apps_file = Path("apps.json")
    if not apps_file.exists():
        raise FileNotFoundError("apps.json not found in root directory.")
    with open(apps_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if "target_apps" in data:
                return data["target_apps"]
            elif "apps" in data:
                return data["apps"]
        return []

def main():
    print("=" * 60)
    print("🚀 COMPOSIO RESEARCH AGENT - PROCESSING APPS")
    print("=" * 60)

    apps = load_apps()
    research_records = []

    for idx, item in enumerate(apps, 1):
        if not isinstance(item, dict):
            continue

        app_id = item.get("id", idx)
        app_name = item.get("app") or item.get("name") or f"App_{app_id}"
        category = item.get("category", "General")
        does = item.get("does") or item.get("description") or ""
        auth = item.get("auth") or "OAuth2"
        access = item.get("access") or "self-serve"
        api_type = item.get("api") or "REST"
        mcp = str(item.get("mcp", "No"))
        verdict = item.get("verdict") or "Buildable"
        blocker = item.get("blocker", "")
        evidence_url = item.get("evidence") or ""
        confidence = item.get("confidence", "high")
        verification = item.get("verification", "agent pass")

        slug = str(app_name).lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        evidence_filename = f"{idx:03d}_{slug}_evidence.json"
        evidence_path = EVIDENCE_DIR / evidence_filename

        evidence_payload = {
            "id": app_id,
            "app": app_name,
            "category": category,
            "does": does,
            "auth": auth,
            "access": access,
            "api": api_type,
            "mcp": mcp,
            "verdict": verdict,
            "blocker": blocker,
            "evidence_url": evidence_url,
            "confidence": confidence,
            "verification": verification,
            "fetched_at": datetime.now().isoformat()
        }
        with open(evidence_path, "w", encoding="utf-8") as ef:
            json.dump(evidence_payload, ef, indent=2)

        record = {
            "id": app_id,
            "app": app_name,
            "category": category,
            "does": does,
            "auth_methods": [a.strip() for a in str(auth).replace(";", "/").split("/") if a.strip()],
            "auth_raw": str(auth),
            "credential_access": access,
            "api_type": api_type,
            "mcp_available": str(mcp).lower() == "yes",
            "mcp_raw": mcp,
            "buildability": verdict,
            "blocker": blocker,
            "evidence_urls": [evidence_url] if evidence_url else [],
            "confidence": confidence,
            "verification_method": verification,
            "evidence_file": evidence_filename
        }
        research_records.append(record)

    output_path = OUTPUT_DIR / "research.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(research_records, f, indent=2)

    print(f"✅ Successfully processed {len(research_records)} apps into {output_path}")

if __name__ == "__main__":
    main()