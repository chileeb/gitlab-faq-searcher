#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict


TEXT_EXTS = {".md", ".mdx", ".txt"}


def run_rg(query: str, root: Path, limit: int) -> List[Dict]:
    cmd = [
        "rg",
        "-n",
        "-i",
        "--hidden",
        "--glob",
        "*.md",
        "--glob",
        "*.mdx",
        "--glob",
        "*.txt",
        query,
        str(root),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or "rg failed")

    results = []
    for line in proc.stdout.splitlines()[:limit]:
        m = re.match(r"^(.*?):(\d+):(.*)$", line)
        if not m:
            continue
        path, line_no, text = m.groups()
        results.append({
            "path": os.path.relpath(path, str(root)),
            "line": int(line_no),
            "text": text.strip(),
        })
    return results


def run_python_scan(query: str, root: Path, limit: int) -> List[Dict]:
    pattern = query.casefold()
    results = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(f, 1):
                    if pattern in line.casefold():
                        results.append({
                            "path": os.path.relpath(path, str(root)),
                            "line": idx,
                            "text": line.strip(),
                        })
                        if len(results) >= limit:
                            return results
        except OSError:
            continue
    return results


def search(query: str, root: Path, limit: int) -> List[Dict]:
    try:
        return run_rg(query, root, limit)
    except FileNotFoundError:
        return run_python_scan(query, root, limit)


def main() -> int:
    parser = argparse.ArgumentParser(description="Search a local GitLab FAQ/docs corpus")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--root", required=True, help="Local corpus root path")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Corpus root not found: {root}", file=sys.stderr)
        return 2

    try:
        results = search(args.query, root, args.limit)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"query": args.query, "root": str(root), "results": results}, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print("NO_MATCH")
        return 0

    print(f"Query: {args.query}")
    print(f"Root: {root}")
    print()
    for i, item in enumerate(results, 1):
        print(f"[{i}] {item['path']}:{item['line']}")
        print(f"    {item['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
