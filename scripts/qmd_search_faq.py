#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description='Search indexed FAQ via qmd')
    parser.add_argument('--collection', required=True)
    parser.add_argument('--query', required=True)
    parser.add_argument('-n', '--limit', type=int, default=5)
    args = parser.parse_args()

    cmd = ['qmd', 'search', '--json', '-n', str(args.limit), args.query]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(json.dumps({'status': 'qmd_missing', 'collection': args.collection, 'query': args.query}, ensure_ascii=False, indent=2))
        return 2

    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        return proc.returncode

    print(proc.stdout)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
