#!/usr/bin/env python3
"""
Status Guard
- Reads ops/STATE.md
- Runs a live proof command
- Outputs strict template:
  Status: ...
  Proof: ...
  Next: ...

Usage:
  python scripts/status_guard.py --status "Dashboard deploy" \
    --proof-cmd "curl -sI https://example.com | head -n 1" \
    --next "Publish final URL"
"""

import argparse
import subprocess
from pathlib import Path

STATE_PATH = Path('/home/bernard/.openclaw/workspace/ops/STATE.md')


def run(cmd: str) -> str:
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    out = (p.stdout or '').strip()
    err = (p.stderr or '').strip()
    merged = out if out else err
    if not merged:
        merged = f"(no output, exit={p.returncode})"
    return f"$ {cmd}\n{merged}\n(exit={p.returncode})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--status', required=True, help='Status line')
    ap.add_argument('--proof-cmd', required=True, help='Live command to prove status')
    ap.add_argument('--next', required=True, help='Next step')
    args = ap.parse_args()

    if not STATE_PATH.exists():
        print('Status: blocked (STATE.md missing)')
        print('Proof: ops/STATE.md not found')
        print('Next: create ops/STATE.md and retry')
        return

    state_head = '\n'.join(STATE_PATH.read_text().splitlines()[:8])
    proof = run(args.proof_cmd)

    print(f"Status: {args.status}")
    print("Proof:")
    print("- STATE.md check:")
    print(state_head)
    print("- Live command:")
    print(proof)
    print(f"Next: {args.next}")


if __name__ == '__main__':
    main()
