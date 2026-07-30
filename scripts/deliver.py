#!/usr/bin/env python3
"""
Piyo 交付物自動上傳腳本。

用法：
  python3 scripts/deliver.py \
    --book PYO-017 --stage S4A --round R1 \
    --title "PYO-017 S4A en-US gate4 證據包" \
    --desc "三檔 draft + QA 二輪 + 回譯 33 頁" \
    --source /path/to/gate_package/ \
    --status pending

  # Green Light 凍結版（自動把同書同站舊 pending → frozen）
  python3 scripts/deliver.py \
    --book PYO-017 --stage S4A --round GL \
    --title "PYO-017 S4A en-US Green Light" \
    --source /path/to/gl_package/ \
    --status frozen --freeze-prior
"""
import argparse, json, os, subprocess, sys, re
from datetime import date
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
MANIFEST = REPO_DIR / "manifest.json"
VALID_STAGES = ["S1", "S2", "S3", "S4A", "S4B", "S5", "S6"]
VALID_ROUNDS = re.compile(r"^(R\d+|GL)$")


def slug(book: str, stage: str, round_: str) -> str:
    b = book.lower().replace("-", "")
    s = stage.lower()
    r = round_.lower()
    return f"{b}-{s}-{r}"


def load_manifest():
    with open(MANIFEST, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        return {"bookNames": {}, "deliveries": data}
    return data


def save_manifest(data):
    with open(MANIFEST, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    f.close()


def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=REPO_DIR,
                        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"git error: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description="Upload a Piyo delivery package")
    ap.add_argument("--book", required=True, help="Book ID, e.g. PYO-017")
    ap.add_argument("--stage", required=True, choices=VALID_STAGES)
    ap.add_argument("--round", required=True, help="R1, R2, ... or GL")
    ap.add_argument("--title", required=True, help="Display title (Chinese)")
    ap.add_argument("--desc", default="", help="One-line description")
    ap.add_argument("--source", required=True, help="Source dir or file to zip")
    ap.add_argument("--status", default="pending", choices=["pending", "frozen"])
    ap.add_argument("--freeze-prior", action="store_true",
                    help="Set prior pending entries for same book+stage to frozen")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = ap.parse_args()

    if not VALID_ROUNDS.match(args.round):
        print(f"Invalid round: {args.round} (use R1, R2, ... or GL)", file=sys.stderr)
        sys.exit(1)

    source = Path(args.source).resolve()
    if not source.exists():
        print(f"Source not found: {source}", file=sys.stderr)
        sys.exit(1)

    task_slug = slug(args.book, args.stage, args.round)
    zip_name = f"{args.book}_{args.stage}_{args.round}.zip"
    pkg_dir = REPO_DIR / task_slug

    print(f"Task slug: {task_slug}")
    print(f"ZIP name:  {zip_name}")

    if args.dry_run:
        print("[dry-run] Would create package and update manifest.")
        return

    git("pull", "origin", "main")

    pkg_dir.mkdir(exist_ok=True)
    zip_path = pkg_dir / zip_name

    if source.is_dir():
        subprocess.run(
            ["zip", "-r", str(zip_path), ".", "-x", "*.DS_Store"],
            cwd=source, check=True, capture_output=True
        )
    else:
        subprocess.run(
            ["zip", "-j", str(zip_path), str(source)],
            check=True, capture_output=True
        )
    print(f"Created: {zip_path.relative_to(REPO_DIR)}")

    data = load_manifest()
    deliveries = data["deliveries"]

    existing = [d for d in deliveries if d.get("id") == task_slug]
    if existing:
        entry = existing[0]
        entry["title"] = args.title
        entry["description"] = args.desc
        entry["date"] = date.today().isoformat()
        entry["files"] = [zip_name]
        entry["status"] = args.status
        entry["round"] = args.round
        print(f"Updated existing entry: {task_slug}")
    else:
        entry = {
            "id": task_slug,
            "title": args.title,
            "date": date.today().isoformat(),
            "description": args.desc,
            "files": [zip_name],
            "book": args.book,
            "stage": args.stage,
            "status": args.status,
            "round": args.round,
        }
        deliveries.append(entry)
        print(f"Added new entry: {task_slug}")

    if args.freeze_prior:
        frozen_count = 0
        for d in deliveries:
            if (d.get("book") == args.book
                    and d.get("stage") == args.stage
                    and d.get("status") == "pending"
                    and d.get("id") != task_slug):
                d["status"] = "frozen"
                frozen_count += 1
        if frozen_count:
            print(f"Froze {frozen_count} prior pending entries for {args.book} {args.stage}")

    save_manifest(data)

    git("add", ".")
    git("commit", "-m", f"add {task_slug}")
    git("push", "origin", "main")

    url = f"https://henrywhuang.github.io/piyo-deliveries/"
    print(f"\nDone. View at: {url}")


if __name__ == "__main__":
    main()
