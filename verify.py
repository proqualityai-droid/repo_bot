import os
import sys
from pathlib import Path
from telethon.sync import TelegramClient

# Color codes
rd, gn, lgn, yw, lrd = (
    "\033[00;31m",
    "\033[00;32m",
    "\033[01;32m",
    "\033[01;33m",
    "\033[01;31m",
)
cn, k, g = "\033[00;36m", "\033[90m", "\033[38;5;130m"


def normalize_phone(phone: str) -> str:
    phone = str(phone).strip()
    if phone.startswith("+"):
        return "+" + "".join(ch for ch in phone if ch.isdigit())
    return "".join(ch for ch in phone if ch.isdigit())


def sanitize_session_name(phone_number: str) -> str:
    cleaned = "".join(ch for ch in phone_number if ch.isdigit())
    return f"session_{cleaned or 'default'}"


def load_accounts(path="reporter_config/accounts.txt"):
    """Load accounts from accounts.txt"""
    accounts_file = Path(path)
    if not accounts_file.exists():
        print(f"{lrd}[!] {path} not found")
        return []

    accounts = []
    with accounts_file.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue
            parts = [p.strip() for p in raw.split(",")]
            if len(parts) < 3:
                continue
            api_id = parts[0]
            api_hash = parts[1]
            phone = parts[2]
            password = parts[3] if len(parts) > 3 else ""
            accounts.append((api_id, api_hash, phone, password))
    return accounts


def remove_account_from_file(phone, path="reporter_config/accounts.txt"):
    """Remove account from accounts.txt"""
    accounts = load_accounts(path)
    target_digits = normalize_phone(phone)

    def digits(p):
        return normalize_phone(p)

    new_accounts = [a for a in accounts if digits(a[2]) != target_digits]
    if len(new_accounts) == len(accounts):
        return False

    acct_file = Path(path)
    lines = []
    for api_id, api_hash, p, password in new_accounts:
        if password:
            lines.append(f"{api_id},{api_hash},{p},{password}\n")
        else:
            lines.append(f"{api_id},{api_hash},{p}\n")
    acct_file.write_text("".join(lines), encoding="utf-8")
    return True


def verify_account(api_id, api_hash, phone, password):
    """Verify a single account. Returns ('ok', data), ('frozen', msg), ('not_authorized', msg), ('error', msg)"""
    session_name = sanitize_session_name(phone)
    try:
        api_id_value = int(api_id)
    except ValueError:
        return ("error", f"Invalid api_id: {api_id}")

    client = None
    try:
        client = TelegramClient(session_name, api_id_value, api_hash)
        client.connect()

        if not client.is_user_authorized():
            return ("not_authorized", "Session not authorized")

        try:
            me = client.get_me()
            username = getattr(me, "username", None) or "N/A"
            uid = getattr(me, "id", None) or "N/A"
            first_name = getattr(me, "first_name", "") or ""
            return ("ok", f"ID={uid}, Username={username}, Name={first_name}")
        except Exception as exc:
            error_str = str(exc).lower()
            if (
                "banned" in error_str
                or "freeze" in error_str
                or "suspended" in error_str
            ):
                return ("frozen", str(exc))
            return ("error", str(exc))
    except Exception as exc:
        error_str = str(exc).lower()
        if "banned" in error_str or "freeze" in error_str or "suspended" in error_str:
            return ("frozen", str(exc))
        return ("error", str(exc))
    finally:
        if client is not None:
            try:
                client.disconnect()
            except Exception:
                pass


def main():
    print(f"\n{lrd}{'='*70}")
    print(f"{lgn}Account Verification Tool{lrd}")
    print(f"{lrd}{'='*70}\n")

    accounts = load_accounts("reporter_config/accounts.txt")
    if not accounts:
        print(f"{lrd}[!] No accounts found in reporter_config/accounts.txt")
        return

    print(f"{lgn}[+] Found {len(accounts)} account(s) to verify\n")

    results = {"ok": [], "frozen": [], "not_authorized": [], "error": []}

    for idx, (api_id, api_hash, phone, password) in enumerate(accounts, 1):
        print(f"{cn}[{idx}/{len(accounts)}] Checking {phone}...", end=" ", flush=True)
        status, msg = verify_account(api_id, api_hash, phone, password)

        if status == "ok":
            print(f"{gn}✓ OK{lrd} - {msg}")
            results["ok"].append((phone, msg))
        elif status == "frozen":
            print(f"{lrd}✗ FROZEN{lrd} - {msg}")
            results["frozen"].append((phone, msg))
        elif status == "not_authorized":
            print(f"{yw}⚠ NOT_AUTHORIZED{lrd} - {msg}")
            results["not_authorized"].append((phone, msg))
        else:
            print(f"{rd}✗ ERROR{lrd} - {msg}")
            results["error"].append((phone, msg))

    print(f"\n{lrd}{'='*70}")
    print(f"{lrd}VERIFICATION SUMMARY{lrd}")
    print(f"{lrd}{'='*70}")
    print(f"{gn}✓ OK: {len(results['ok'])}{lrd}")
    print(f"{lrd}✗ FROZEN: {len(results['frozen'])}{lrd}")
    print(f"{yw}⚠ NOT_AUTHORIZED: {len(results['not_authorized'])}{lrd}")
    print(f"{rd}✗ ERROR: {len(results['error'])}{lrd}")

    if results["frozen"]:
        print(f"\n{lrd}Frozen account(s) found:{lrd}")
        for phone, msg in results["frozen"]:
            print(f"  - {phone}: {msg}")
        print(f"\n{lgn}Would you like to remove frozen accounts? (y/n): {k}", end="")
        choice = input().strip().lower()
        if choice in ("y", "yes"):
            for phone, _ in results["frozen"]:
                if remove_account_from_file(phone):
                    print(f"{gn}[+] Removed {phone} from accounts.txt{lrd}")
                else:
                    print(f"{rd}[!] Failed to remove {phone}{lrd}")

    if results["not_authorized"]:
        print(f"\n{yw}Not authorized account(s):{lrd}")
        for phone, msg in results["not_authorized"]:
            print(f"  - {phone}: {msg}")
        print(f"\n{lgn}These accounts need re-login (session expired or invalid).{lrd}")

    print(f"\n{lrd}{'='*70}\n")


if __name__ == "__main__":
    main()
