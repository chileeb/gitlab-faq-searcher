#!/usr/bin/env python3
import json
import shutil


def main() -> int:
    qmd = shutil.which('qmd')
    result = {
        'qmd_found': bool(qmd),
        'qmd_path': qmd,
        'status': 'ready' if qmd else 'missing',
        'next_step': None if qmd else 'Install or initialize qmd before indexing'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if qmd else 2


if __name__ == '__main__':
    raise SystemExit(main())
