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

def main():
    print("=" * 60)
    print("🔎 COMPOSIO VERIFICATION AGENT - AUDITING INTEGRITY")
    print("=" * 60)

    research_path = OUTPUT_DIR / "research.json"
    if not research_path.exists():
        print(f"❌ Error: {research_path} does not exist.")
        return

    with open(research_path, "r", encoding="utf-8") as f:
        research = json.load(f)

    verifications = []
    passed = 0

    for item in research:
        app_name = item["app"]
        ev_file = item.get("evidence_file", "")
        ev_path = EVIDENCE_DIR / ev_file if ev_file else None

        valid = True
        issues = []

        if not ev_path or not ev_path.exists():
            valid = False
            issues.append(f"Missing evidence file: {ev_file}")
        else:
            try:
                with open(ev_path, "r", encoding="utf-8") as ef:
                    ev_data = json.load(ef)
                    if ev_data.get("app") != app_name:
                        valid = False
                        issues.append("App name mismatch in evidence")
            except Exception as e:
                valid = False
                issues.append(f"JSON load error: {e}")

        if valid:
            passed += 1

        verifications.append({
            "id": item["id"],
            "app": app_name,
            "category": item["category"],
            "verified": valid,
            "issues": issues,
            "verified_at": datetime.now().isoformat()
        })

    total = len(research)
    score = round(passed / total * 100, 2) if total else 0

    output_payload = {
        "metadata": {
            "verified_at": datetime.now().isoformat(),
            "total_apps": total,
            "passed_checks": passed,
            "failed_checks": total - passed,
            "integrity_score_pct": score,
            "status": "PASSED" if score >= 90.0 else "WARNING"
        },
        "verifications": verifications
    }

    output_path = OUTPUT_DIR / "verification_results.json"
    with open(output_path, "w", encoding="utf-8") as vf:
        json.dump(output_payload, vf, indent=2)

    print(f"✅ Verified {passed}/{total} apps. Integrity Score: {score}%")
    print(f"📄 Saved to {output_path}")

if __name__ == "__main__":
    main()
