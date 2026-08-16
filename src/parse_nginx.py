#!/usr/bin/env python3
"""Transforme une ligne d'access.log nginx en champs structurés."""
import re
from datetime import datetime

# Regex du format "combined" de nginx (le format par défaut).
LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+) '      # IP source
    r'\S+ \S+ '                          # identité et user (toujours "-")
    r'\[(?P<time>[^\]]+)\] '             # timestamp entre crochets
    r'"(?P<method>\S+) (?P<path>\S+) [^"]*" '  # "MÉTHODE chemin PROTOCOLE"
    r'(?P<status>\d+) '                  # code de statut HTTP
    r'\d+ '                              # taille de la réponse
    r'"[^"]*" '                          # referer
    r'"(?P<agent>[^"]*)"'                # user-agent
)

# Chemins sensibles : leur présence indique une tentative de scan/exploit.
SUSPICIOUS_PATTERNS = re.compile(
    r"(\.env|\.git|wp-login|phpmyadmin|admin|etc/passwd|"
    r"\.\./|<script|union\s+select|'\s+or\s+|%27|%3c)",
    re.IGNORECASE,
)


def parse_nginx_time(time_str):
    """Convertit '15/Aug/2026:18:39:51 +0000' en ISO."""
    dt = datetime.strptime(time_str, "%d/%b/%Y:%H:%M:%S %z")
    return dt.isoformat(timespec="seconds")


def classify(path, status):
    """Détermine event_type et severity selon le chemin et le code."""
    suspect = bool(SUSPICIOUS_PATTERNS.search(path))

    if suspect and status == 400:
        return "web_malformed_request", "high"
    if suspect:
        return "web_suspicious_scan", "high"
    if status == 404:
        return "web_not_found", "low"
    if status >= 500:
        return "web_server_error", "medium"
    if 200 <= status < 300:
        return "web_normal", "info"
    return "web_other", "low"


def parse_nginx_line(line):
    """Analyse une ligne d'access.log. Retourne un dict, ou None."""
    match = LOG_PATTERN.search(line)
    if not match:
        return None

    status = int(match.group("status"))
    path = match.group("path")
    event_type, severity = classify(path, status)

    return {
        "event_type": event_type,
        "severity": severity,
        "source_ip": match.group("ip"),
        "timestamp": parse_nginx_time(match.group("time")),
        "source": "web",
        "path": path,
        "status": status,
        "raw": line.strip(),
    }


if __name__ == "__main__":
    exemples = [
        '192.168.1.25 - - [15/Aug/2026:18:39:51 +0000] "GET / HTTP/1.1" 200 615 "-" "curl/7.81.0"',
        '192.168.1.25 - - [15/Aug/2026:17:04:49 +0000] "GET /.env HTTP/1.1" 404 162 "-" "curl/7.81.0"',
        '192.168.1.25 - - [15/Aug/2026:17:04:49 +0000] "GET /../../etc/passwd HTTP/1.1" 400 166 "-" "-"',
        '192.168.1.25 - - [15/Aug/2026:17:04:49 +0000] "GET /index.php?id=1%27+OR+%271 HTTP/1.1" 404 162 "-" "curl/7.81.0"',
        '192.168.1.25 - - [15/Aug/2026:14:04:44 +0000] "GET /contact HTTP/1.1" 404 162 "-" "curl/7.81.0"',
    ]
    for ligne in exemples:
        r = parse_nginx_line(ligne)
        print(f"{r['source_ip']:15}{r['status']} {r['path'][:32]:34} -> {r['event_type']:22} ({r['severity']})")
