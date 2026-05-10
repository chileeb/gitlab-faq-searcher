#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-{2,}', '-', text).strip('-')
    return text or 'issue'


def project_ref(project: str) -> str:
    if project.isdigit():
        return project
    return urllib.parse.quote(project, safe='')


def build_url(base_url: str, project: str, state: str, labels: list[str], per_page: int, page: int) -> str:
    query = {
        'state': state,
        'per_page': str(per_page),
        'page': str(page),
        'order_by': 'updated_at',
        'sort': 'desc',
    }
    if labels:
        query['labels'] = ','.join(labels)
    return f"{base_url.rstrip('/')}/api/v4/projects/{project_ref(project)}/issues?{urllib.parse.urlencode(query)}"


def fetch_json(url: str, token: Optional[str]):
    req = urllib.request.Request(url)
    if token:
        req.add_header('PRIVATE-TOKEN', token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8')), resp.headers


def render_issue(issue: dict) -> str:
    labels = issue.get('labels') or []
    body = issue.get('description') or ''
    return f"""---
title: {issue.get('title', '').strip()}
iid: {issue.get('iid')}
issue_id: {issue.get('id')}
state: {issue.get('state')}
created_at: {issue.get('created_at')}
updated_at: {issue.get('updated_at')}
web_url: {issue.get('web_url')}
author: {(issue.get('author') or {}).get('name', '')}
labels: {json.dumps(labels, ensure_ascii=False)}
---

# {issue.get('title', '').strip()}

**Issue:** {issue.get('web_url')}

## Description

{body}
"""


def write_issue(out: Path, issue: dict) -> Path:
    iid = issue.get('iid')
    title = issue.get('title') or ''
    name = f"issue-{iid}-{slugify(title)[:80]}.md"
    path = out / name
    path.write_text(render_issue(issue), encoding='utf-8')
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description='Sync GitLab issues into local markdown files')
    parser.add_argument('--project', required=True, help='GitLab project path or numeric id')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--base-url', default='https://gitlab.com', help='GitLab base URL')
    parser.add_argument('--token-env', default='GITLAB_TOKEN', help='Env var holding GitLab token')
    parser.add_argument('--label', action='append', default=[], help='Optional issue label filter')
    parser.add_argument('--state', default='opened', help='Issue state filter')
    parser.add_argument('--per-page', type=int, default=20, help='Max issues to fetch per page')
    parser.add_argument('--max-pages', type=int, default=1, help='How many pages to fetch')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get(args.token_env)

    if not token and args.base_url.rstrip('/') != 'https://gitlab.com':
        print(json.dumps({'status': 'missing_token', 'token_env': args.token_env}, ensure_ascii=False, indent=2))
        return 2

    all_issues = []
    urls = []
    try:
        for page in range(1, args.max_pages + 1):
            url = build_url(args.base_url, args.project, args.state, args.label, args.per_page, page)
            urls.append(url)
            issues, _headers = fetch_json(url, token)
            if not issues:
                break
            all_issues.extend(issues)
            if len(issues) < args.per_page:
                break
    except urllib.error.HTTPError as e:
        detail = e.read().decode('utf-8', errors='ignore') if hasattr(e, 'read') else ''
        print(json.dumps({'status': 'http_error', 'code': e.code, 'detail': detail[:500]}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    except Exception as e:
        print(json.dumps({'status': 'error', 'detail': str(e)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    written = []
    if not args.dry_run:
        for issue in all_issues:
            path = write_issue(out, issue)
            written.append(str(path))

    print(json.dumps({
        'status': 'ok',
        'project': args.project,
        'base_url': args.base_url,
        'labels': args.label,
        'state': args.state,
        'fetched': len(all_issues),
        'written': written,
        'out': str(out),
        'urls': urls,
        'dry_run': args.dry_run,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
