import os
import socket
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from runtime_env import clean_env_value, is_railway


DEFAULT_RSS3_ENV_PATH = (
    "/home/baba2-mainoffice/Documents/Obsidian Vault/Agents/Secrets/rss3-node-linode.env"
)
HTTP_TIMEOUT_SECONDS = 5


def _load_rss3_env() -> None:
    if is_railway():
        return

    env_path = os.environ.get("RSS3_ENV_PATH", DEFAULT_RSS3_ENV_PATH)
    try:
        with open(env_path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if "=" not in line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if not os.environ.get(key):
                    os.environ[key] = clean_env_value(value)
    except FileNotFoundError:
        pass


_load_rss3_env()


def _get_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def _mask_host(value: str) -> str:
    if not value:
        return ""
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.hostname or parsed.netloc}"
    return value


def _probe_url(url: str) -> dict:
    result = {
        "url": url,
        "ok": False,
        "status": None,
        "latency_ms": None,
        "summary": "",
    }
    try:
        request = Request(url, headers={"User-Agent": "Aragamago-RSS3-Diagnostics/1.0"})
        started = time.time()
        with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            body = response.read(400).decode("utf-8", errors="replace")
            result["ok"] = 200 <= response.status < 400
            result["status"] = response.status
            result["latency_ms"] = int((time.time() - started) * 1000)
            result["summary"] = body.strip().replace("\n", " ")[:140]
            return result
    except HTTPError as error:
        result["status"] = error.code
        result["summary"] = str(error)
        return result
    except URLError as error:
        result["summary"] = str(error.reason)
        return result
    except Exception as error:
        result["summary"] = str(error)
        return result


def _probe_discovery_endpoint(base_url: str) -> dict:
    if not base_url:
        return {
            "configured": False,
            "ok": False,
            "checked_url": "",
            "status": None,
            "latency_ms": None,
            "summary": "NODE_CONFIG_DISCOVERY_SERVER_ENDPOINT missing",
        }

    candidates = [base_url.rstrip("/")]
    for suffix in ("/health", "/healthz", "/status", "/metrics"):
        candidates.append(base_url.rstrip("/") + suffix)

    best = None
    for candidate in candidates:
        probe = _probe_url(candidate)
        if best is None:
            best = probe
        if probe["ok"]:
            return {
                "configured": True,
                "ok": True,
                "checked_url": probe["url"],
                "status": probe["status"],
                "latency_ms": probe["latency_ms"],
                "summary": probe["summary"] or "reachable",
            }
    return {
        "configured": True,
        "ok": False,
        "checked_url": best["url"] if best else base_url,
        "status": best["status"] if best else None,
        "latency_ms": best["latency_ms"] if best else None,
        "summary": best["summary"] if best else "probe failed",
    }


def _dns_check(hostname: str) -> dict:
    try:
        infos = socket.getaddrinfo(hostname, None)
        addresses = sorted({info[4][0] for info in infos if info[4]})
        return {"ok": bool(addresses), "addresses": addresses[:4], "error": ""}
    except Exception as error:
        return {"ok": False, "addresses": [], "error": str(error)}


def _classify_database(database_url: str) -> dict:
    if not database_url:
        return {
            "configured": False,
            "target": "missing",
            "host": "",
            "is_supabase": False,
            "is_local": False,
        }

    parsed = urlparse(database_url)
    host = parsed.hostname or ""
    return {
        "configured": True,
        "target": host or "unknown",
        "host": host,
        "is_supabase": "supabase" in host,
        "is_local": host in {"localhost", "127.0.0.1", "rss3_local_db", "postgres"},
    }


def get_rss3_status() -> dict:
    discovery_endpoint = _get_env("NODE_CONFIG_DISCOVERY_SERVER_ENDPOINT")
    database_url = _get_env("NODE_DATABASE_URL", "DATABASE_URI", "DB_CONNECTION")
    access_token = _get_env("NODE_CONFIG_DISCOVERY_SERVER_ACCESS_TOKEN", "RSS3_ACCESS_TOKEN")
    operator_address = _get_env("NODE_CONFIG_DISCOVERY_OPERATOR_EVM_ADDRESS")
    operator_signature = _get_env(
        "NODE_CONFIG_DISCOVERY_OPERATOR_SIGNATURE",
        "NODE_DISCOVERY_OPERATOR_SIGNATURE",
    )
    neynar_signer = _get_env("NODE_NEYNAR_SIGNER_UUID")

    discovery = _probe_discovery_endpoint(discovery_endpoint)
    gi_dns = _dns_check("gi.rss3.io")
    database = _classify_database(database_url)

    warnings = []
    if database["is_supabase"]:
        warnings.append("Database still points at Supabase instead of Linode-local Postgres.")
    if not gi_dns["ok"]:
        warnings.append("gi.rss3.io DNS failed; broadcaster/global indexing may be blocked upstream.")
    if not discovery["ok"]:
        warnings.append("Discovery endpoint probe failed.")
    if not access_token:
        warnings.append("Discovery access token missing.")
    if not operator_address or not operator_signature:
        warnings.append("Operator registration credentials incomplete.")

    if not gi_dns["ok"]:
        global_indexing = "blocked"
    elif discovery["ok"] and access_token and operator_address and operator_signature:
        global_indexing = "ready"
    else:
        global_indexing = "degraded"

    return {
        "discovery_endpoint": _mask_host(discovery_endpoint),
        "discovery": discovery,
        "database": database,
        "global_indexing": global_indexing,
        "gi_dns": gi_dns,
        "has_access_token": bool(access_token),
        "has_operator_address": bool(operator_address),
        "has_operator_signature": bool(operator_signature),
        "has_neynar_signer_uuid": bool(neynar_signer),
        "local_env_path": str(Path(os.environ.get("RSS3_ENV_PATH", DEFAULT_RSS3_ENV_PATH))),
        "warnings": warnings,
    }


def format_rss3_status_markdown() -> str:
    status = get_rss3_status()
    icon = {
        "ready": "🟢",
        "degraded": "🟡",
        "blocked": "🔴",
    }.get(status["global_indexing"], "⚪")

    discovery = status["discovery"]
    database = status["database"]
    gi_dns = status["gi_dns"]

    lines = [
        f"{icon} *RSS3 Node 97 Diagnostic*",
        "",
        f"• Global indexing: `{status['global_indexing']}`",
        f"• Discovery endpoint: `{status['discovery_endpoint'] or 'missing'}`",
        f"• Discovery probe: `{'ok' if discovery['ok'] else 'failed'}`"
        + (f" (`{discovery['status']}`)" if discovery["status"] else ""),
        f"• `gi.rss3.io` DNS: `{'ok' if gi_dns['ok'] else 'failed'}`",
        f"• Database target: `{database['target'] or 'missing'}`",
        f"• Access token present: `{'yes' if status['has_access_token'] else 'no'}`",
        f"• Operator creds present: `{'yes' if status['has_operator_address'] and status['has_operator_signature'] else 'no'}`",
        f"• Neynar signer UUID present: `{'yes' if status['has_neynar_signer_uuid'] else 'no'}`",
    ]

    if gi_dns["addresses"]:
        lines.append(f"• `gi.rss3.io` addresses: `{', '.join(gi_dns['addresses'])}`")
    if discovery["summary"]:
        lines.append(f"• Discovery note: `{discovery['summary']}`")
    if status["warnings"]:
        lines.append("")
        lines.append("*Warnings*")
        for warning in status["warnings"][:4]:
            lines.append(f"• {warning}")

    return "\n".join(lines)
