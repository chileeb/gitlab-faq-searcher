# GitLab FAQ Searcher Notes

## Expected Inputs

Support one of these sources:
- local docs/FAQ corpus path
- GitLab project repository clone
- GitLab wiki export
- future: GitLab API-backed search

## Preferred First Version

Start with local corpus retrieval because it is deterministic, fast, and easy to test.

## Query Normalization

When searching:
- keep product names and exact errors intact
- try exact phrase first when the query contains a distinct message
- fall back to keyword search if exact phrase is weak
- preserve version numbers, flags, env vars, and code identifiers

## Output Quality Bar

Good answers should:
- cite the matched file/path
- include a short excerpt
- avoid claims that are not backed by retrieved text
- say low confidence when matches are weak or indirect

## Next Planned Expansion

- add GitLab REST/API search mode
- add heading-aware ranking
- add markdown title extraction
- add answer formatter for top match summaries
