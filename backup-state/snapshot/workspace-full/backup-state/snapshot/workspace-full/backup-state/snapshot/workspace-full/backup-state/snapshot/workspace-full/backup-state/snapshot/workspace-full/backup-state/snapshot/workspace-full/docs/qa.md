# QA Check Script

## Script

`./scripts/qa-check.sh`

## What it validates

- HTTP response for:
  - `/`
  - `/assistant-dashboard/`
  - `/pauleauz-landing/`
- JavaScript syntax check:
  - `node --check assistant-dashboard/app.js`

## Usage

From the repository root:

```bash
./scripts/qa-check.sh
```

Default base URL is `http://127.0.0.1:8080`.

You can override it either way:

```bash
./scripts/qa-check.sh http://127.0.0.1:5500
```

or

```bash
BASE_URL=http://127.0.0.1:5500 ./scripts/qa-check.sh
```

## Exit codes

- `0` when all checks pass
- `1` when one or more checks fail
