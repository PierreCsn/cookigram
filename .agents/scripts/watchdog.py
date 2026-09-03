#!/usr/bin/env python3
"""
CookiGram Multi-Agent Watchdog & Claim Monitor.
Detects hung agent processes, expired claims, and coordination deadlocks.
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CLAIMS_FILE = REPO_ROOT / ".agents" / "claims.json"
MAX_INACTIVE_MINUTES = 15


def load_claims() -> dict:
    if not CLAIMS_FILE.exists():
        return {"version": 1, "active_claims": {}, "completed_claims": []}
    try:
        with open(CLAIMS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to read {CLAIMS_FILE}: {e}", file=sys.stderr)
        return {"version": 1, "active_claims": {}, "completed_claims": []}


def save_claims(data: dict) -> None:
    try:
        with open(CLAIMS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save {CLAIMS_FILE}: {e}", file=sys.stderr)


def check_claims(data: dict, cleanup: bool = False) -> list[dict]:
    active = data.get("active_claims", {})
    now = datetime.datetime.now(datetime.UTC)
    stale = []

    print(f"=== Claims Actifs ({len(active)}) ===")
    for issue_id, claim in list(active.items()):
        agent = claim.get("agent", "Unknown")
        branch = claim.get("branch", "Unknown")
        status = claim.get("status", "in_progress")
        claimed_at_str = claim.get("last_heartbeat") or claim.get("claimed_at")

        is_stale = False
        if claimed_at_str:
            try:
                claimed_dt = datetime.datetime.fromisoformat(claimed_at_str)
                age_min = (now - claimed_dt).total_seconds() / 60.0
                if age_min > MAX_INACTIVE_MINUTES and status != "pr_open":
                    is_stale = True
            except Exception:
                age_min = 0
        else:
            age_min = 0

        flag = "[STALE]" if is_stale else "[OK]"
        print(f"  {flag} Issue #{issue_id}: {agent} on '{branch}' ({status}) — Âge: {age_min:.1f} min")

        if is_stale:
            stale.append(claim)
            if cleanup:
                print(f"    -> Libération automatique du claim #{issue_id} (inactivité > {MAX_INACTIVE_MINUTES}m)")
                claim["status"] = "timed_out"
                data.setdefault("completed_claims", []).append(claim)
                del active[issue_id]

    if cleanup and stale:
        save_claims(data)

    return stale


def check_processes(kill_hung: bool = False) -> list[int]:
    print("\n=== Processus Agents Détectés ===")
    out = subprocess.getoutput(
        "ps -eo pid,pcpu,pmem,etime,comm,args | grep -E '(opencode|gemini)' | grep -v grep | grep -v watchdog"
    )
    lines = [line.strip() for line in out.splitlines() if line.strip()]

    hung_pids = []
    if not lines:
        print("  Aucun processus d'agent en cours d'exécution.")
        return hung_pids

    for line in lines:
        parts = line.split(maxsplit=5)
        if len(parts) >= 6:
            pid, pcpu, pmem, etime, comm, args = parts
            print(f"  PID {pid}: {comm} ({pcpu}% CPU, {pmem}% MEM, uptime: {etime})")

            # Check for known hung conditions (e.g. rate limit in opencode log)
            if "opencode" in comm:
                log_path = Path.home() / ".local/share/opencode/log/opencode.log"
                if log_path.exists():
                    tail = subprocess.getoutput(f"tail -n 20 {log_path}")
                    if "Rate limit exceeded" in tail:
                        print(f"    ⚠️ PID {pid} a rencontré un Rate Limit dans son log actif!")
                        hung_pids.append(int(pid))

    if kill_hung and hung_pids:
        for pid in hung_pids:
            print(f"    -> Neutralisation du processus bloqué PID {pid}...")
            subprocess.run(["kill", "-9", str(pid)], check=False)

    return hung_pids


def main():
    parser = argparse.ArgumentParser(description="CookiGram Multi-Agent Watchdog")
    parser.add_argument("--cleanup", action="store_true", help="Libérer les claims expirés et tuer les process bloqués")
    args = parser.parse_args()

    claims_data = load_claims()
    check_claims(claims_data, cleanup=args.cleanup)
    check_processes(kill_hung=args.cleanup)


if __name__ == "__main__":
    main()
