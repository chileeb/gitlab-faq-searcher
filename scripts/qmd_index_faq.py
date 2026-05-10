#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Prepare qmd indexing plan for FAQ corpus')
    parser.add_argument('--source', required=True, help='FAQ source directory')
    parser.add_argument('--collection', required=True, help='qmd collection name')
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    result = {
        'source': str(source),
        'collection': args.collection,
        'source_exists': source.exists(),
        'status': 'stub'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if source.exists() else 2


if __name__ == '__main__':
    raise SystemExit(main())
