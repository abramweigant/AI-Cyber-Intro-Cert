#!/usr/bin/env python3
"""Mint, list, revoke and rotate student tokens for the AI-Cyber gateway.

Only SHA-256 hashes are stored. The plaintext token is printed once, at mint
time, and cannot be recovered afterwards -- if a student loses theirs, rotate.
That is deliberate: Module 6 Section 1.1 tells students the token is a real
credential, and a credential store you can read back is not one.

  ./issue_token.py mint  alice bob carol      # or: mint --count 20 --prefix stu
  ./issue_token.py list
  ./issue_token.py revoke bob
  ./issue_token.py enable bob
  ./issue_token.py rotate bob
  ./issue_token.py remove bob

The gateway reloads tokens.json when its mtime changes, so none of this needs
a service restart.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import sys
from datetime import datetime, timezone

DEFAULT_PATH = os.environ.get("TOKENS_FILE", "/etc/aicyber-gateway/tokens.json")
TOKEN_BYTES = 24                     # 32 chars of urlsafe base64


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def load(path: str) -> dict:
    if not os.path.exists(path):
        return {"students": []}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, list):
        data = {"students": data}
    data.setdefault("students", [])
    return data


def save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)      # 600
    print(f"\nwrote {path} (mode 600, {len(data['students'])} students)")


def find(data: dict, sid: str) -> dict | None:
    return next((s for s in data["students"] if s.get("student_id") == sid), None)


def cmd_mint(args) -> int:
    data = load(args.path)
    ids = list(args.student_ids)
    if args.count:
        width = len(str(args.count))
        ids += [f"{args.prefix}{i:0{width}d}" for i in range(1, args.count + 1)]
    if not ids:
        print("nothing to do: pass student ids or --count", file=sys.stderr)
        return 2

    minted = []
    for sid in ids:
        if find(data, sid):
            print(f"  skip   {sid} (already exists -- use rotate)", file=sys.stderr)
            continue
        token = secrets.token_urlsafe(TOKEN_BYTES)
        data["students"].append({
            "student_id": sid,
            "token_hash": hash_token(token),
            "disabled": False,
            "issued": now(),
            "note": args.note,
        })
        minted.append((sid, token))

    if not minted:
        return 1
    save(args.path, data)
    print("\nGive each student ONLY their own line. These are shown once.\n")
    print(f"  {'student':<16}  token")
    print(f"  {'-'*16}  {'-'*32}")
    for sid, token in minted:
        print(f"  {sid:<16}  {token}")
    print("\nEach student puts theirs in .env as:  LLM_API_KEY=<token>")
    return 0


def cmd_list(args) -> int:
    data = load(args.path)
    if not data["students"]:
        print("no students")
        return 0
    print(f"  {'student':<16}{'state':<10}{'issued':<22}note")
    print(f"  {'-'*16}{'-'*10}{'-'*22}{'-'*20}")
    for s in sorted(data["students"], key=lambda x: x.get("student_id", "")):
        state = "revoked" if s.get("disabled") else "active"
        print(f"  {s.get('student_id',''):<16}{state:<10}"
              f"{s.get('issued',''):<22}{s.get('note','')}")
    active = sum(1 for s in data["students"] if not s.get("disabled"))
    print(f"\n{active} active / {len(data['students'])} total")
    return 0


def _set_disabled(args, disabled: bool, label: str) -> int:
    data = load(args.path)
    s = find(data, args.student_id)
    if not s:
        print(f"no such student: {args.student_id}", file=sys.stderr)
        return 1
    s["disabled"] = disabled
    s[f"{label}_at"] = now()
    save(args.path, data)
    print(f"{args.student_id} is now {'revoked' if disabled else 'active'}")
    return 0


def cmd_revoke(args): return _set_disabled(args, True, "revoked")
def cmd_enable(args): return _set_disabled(args, False, "enabled")


def cmd_rotate(args) -> int:
    data = load(args.path)
    s = find(data, args.student_id)
    if not s:
        print(f"no such student: {args.student_id}", file=sys.stderr)
        return 1
    token = secrets.token_urlsafe(TOKEN_BYTES)
    s["token_hash"] = hash_token(token)
    s["disabled"] = False
    s["rotated"] = now()
    save(args.path, data)
    print(f"\nnew token for {args.student_id} (shown once):\n\n  {token}\n")
    print("Their old token stops working immediately.")
    return 0


def cmd_remove(args) -> int:
    data = load(args.path)
    before = len(data["students"])
    data["students"] = [s for s in data["students"]
                        if s.get("student_id") != args.student_id]
    if len(data["students"]) == before:
        print(f"no such student: {args.student_id}", file=sys.stderr)
        return 1
    save(args.path, data)
    print(f"removed {args.student_id}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--path", default=DEFAULT_PATH, help=f"tokens file (default {DEFAULT_PATH})")
    sub = p.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("mint", help="create tokens for new students")
    m.add_argument("student_ids", nargs="*")
    m.add_argument("--count", type=int, help="also mint N generated ids")
    m.add_argument("--prefix", default="student", help="prefix for --count ids")
    m.add_argument("--note", default="", help="free-text note stored with the entry")
    m.set_defaults(func=cmd_mint)

    sub.add_parser("list", help="show all students").set_defaults(func=cmd_list)

    for name, fn, helptext in (("revoke", cmd_revoke, "disable a token"),
                               ("enable", cmd_enable, "re-enable a token"),
                               ("rotate", cmd_rotate, "replace a token"),
                               ("remove", cmd_remove, "delete the entry")):
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("student_id")
        sp.set_defaults(func=fn)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
