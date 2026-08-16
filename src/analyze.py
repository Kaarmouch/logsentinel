#!/usr/bin/env python3
"""LogSentinel — analyse unifiée des événements SSH (journald) et web (nginx)."""
import os
from collections import Counter, defaultdict
from datetime import datetime
import json

from read_journal import read_ssh_events
from parse_ssh import parse_ssh_message
from parse_nginx import parse_nginx_line

NGINX_LOG = os.environ.get("NGINX_LOG", "/var/log/nginx/access.log")


def to_iso(realtime_timestamp):
    seconds = int(realtime_timestamp) / 1_000_000
    return datetime.fromtimestamp(seconds).isoformat(timespec="seconds")


def collect_ssh(since="1 day ago"):
    out = []
    for event in read_ssh_events(since=since):
        parsed = parse_ssh_message(event.get("MESSAGE", ""))
        if parsed is None:
            continue
        parsed["timestamp"] = to_iso(event["__REALTIME_TIMESTAMP"])
        parsed["source"] = "ssh"
        parsed["raw"] = event["MESSAGE"]
        out.append(parsed)
    return out


def collect_web(path=NGINX_LOG):
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                parsed = parse_nginx_line(line)
                if parsed is not None:
                    out.append(parsed)
    except FileNotFoundError:
        print(f"(access.log introuvable : {path})")
    return out


def analyze(since="1 day ago"):
    return collect_ssh(since=since) + collect_web()


def report(events):
    print(f"=== {len(events)} événements analysés (SSH + web) ===\n")

    par_source = Counter(e["source"] for e in events)
    print("Par source :", dict(par_source))

    par_type = Counter(e["event_type"] for e in events)
    print("\nPar type :")
    for t, c in par_type.most_common():
        print(f"  {c:4}  {t}")

    print("\n=== Profil par IP (toutes sources confondues) ===")
    par_ip = defaultdict(lambda: {"total": 0, "ssh_fail": 0, "web_scan": 0, "normal": 0})
    for e in events:
        p = par_ip[e["source_ip"]]
        p["total"] += 1
        if e["severity"] in ("high", "critical") and e["source"] == "ssh":
            p["ssh_fail"] += 1
        if e["severity"] == "high" and e["source"] == "web":
            p["web_scan"] += 1
        if e["severity"] == "info":
            p["normal"] += 1

    for ip, p in sorted(par_ip.items(), key=lambda x: -x[1]["total"]):
        flags = []
        if p["ssh_fail"] >= 10:
            flags.append("BRUTEFORCE-SSH")
        if p["web_scan"] >= 3:
            flags.append("SCAN-WEB")
        alerte = "  <<< " + " + ".join(flags) if flags else ""
        print(f"  {ip:15} total={p['total']:4} ssh_fail={p['ssh_fail']:3} "
              f"web_scan={p['web_scan']:3} normal={p['normal']:3}{alerte}")

def save_json(events, path="events.json"):
    """Écrit les événements normalisés dans un fichier JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"\n{len(events)} événements écrits dans {path}")

if __name__ == "__main__":
    events = analyze(since="1 day ago")
    report(events)
    save_json(events, path="events.json")
