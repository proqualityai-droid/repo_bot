import os
import time
import platform
import sys
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path
import threading
import random

try:
    from telethon.sync import TelegramClient
    from telethon import functions
    from telethon.tl import types
    from telethon.errors import SessionPasswordNeededError
except ImportError:
    os.system(f"{sys.executable} -m pip install telethon")
    from telethon.sync import TelegramClient
    from telethon import functions
    from telethon.tl import types
    from telethon.errors import SessionPasswordNeededError

try:
    from prettytable import PrettyTable
except ImportError:
    os.system(f"{sys.executable} -m pip install prettytable")
    from prettytable import PrettyTable

try:
    from colorama import init

    init()
except ImportError:
    pass


def re(text):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(0.001)


rd, gn, lgn, yw, lrd, be, pe = (
    "\033[00;31m",
    "\033[00;32m",
    "\033[01;32m",
    "\033[01;33m",
    "\033[01;31m",
    "\033[94m",
    "\033[01;35m",
)
cn, k, g = "\033[00;36m", "\033[90m", "\033[38;5;130m"


def clear():
    if "Windows" in platform.uname().system:
        os.system("cls")
    else:
        os.system("clear")


print(f"{lrd}")
t = PrettyTable([f"{cn}Number{lrd}", f"{cn}Method{lrd}"])
t.add_row([f"{lgn}1{lrd}", f"{gn}Report Spam{lrd}"])
t.add_row([f"{lgn}2{lrd}", f"{gn}Report Other{lrd}"])
t.add_row([f"{lgn}3{lrd}", f"{gn}Report Violence{lrd}"])
t.add_row([f"{lgn}4{lrd}", f"{gn}Report Pornography{lrd}"])
t.add_row([f"{lgn}5{lrd}", f"{gn}Report Copyright{lrd}"])
t.add_row([f"{lgn}6{lrd}", f"{gn}Report Fake{lrd}"])
t.add_row([f"{lgn}7{lrd}", f"{gn}Report Geo Irrelevant{lrd}"])
t.add_row([f"{lgn}8{lrd}", f"{gn}Report Illegal Drugs{lrd}"])
t.add_row([f"{lgn}9{lrd}", f"{gn}Report Personal Details{lrd}"])
t.add_row([f"{lgn}10{lrd}", f"{gn}Report Child Abuse{lrd}"])

account = rf"""{k}
 ____                             _               
|  _ \   ___  _ __    ___   _ __ | |_   ___  _ __ 
| |_) | / _ \| '_ \  / _ \ | '__|| __| / _ \| '__|
|  _ < |  __/| |_) || (_) || |   | |_ |  __/| |    {cn}Channel{k}
|_| \_\ \___|| .__/  \___/ |_|    \__| \___||_|   
             |_|   

	{lrd}[{lgn}+{lrd}] {gn}Channel : {lgn}@Esfelurm	
"""


def find_accounts_file(path="accounts.txt"):
    candidates = [
        Path(path),
        Path(__file__).parent / path,
        Path(__file__).parent.parent / path,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_ban_file(path="reporter_config/ban.txt"):
    candidates = [
        Path(path),
        Path(__file__).parent / path,
        Path(__file__).parent.parent / path,
        Path.cwd() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Create a default ban file path if none exists yet.
    default_path = Path(__file__).parent / path
    default_path.parent.mkdir(parents=True, exist_ok=True)
    default_path.write_text(
        "# Ban.txt - Add user accounts to report automatically\n"
        "# Format: username:method1,method2,method3 OR username:all\n"
        "# Report Methods:\n"
        "# 1 = Report Spam\n"
        "# 2 = Report Other\n"
        "# 3 = Report Violence\n"
        "# 4 = Report Pornography\n"
        "# 5 = Report Copyright\n"
        "# 6 = Report Fake\n"
        "# 7 = Report Geo Irrelevant\n"
        "# 8 = Report Illegal Drugs\n"
        "# 9 = Report Personal Details\n"
        "# 10 = Report Child Abuse\n"
        "#\n"
        "# Add your target users below:\n\n",
        encoding="utf-8",
    )
    return default_path


def load_accounts(path="accounts.txt"):
    accounts_file = find_accounts_file(path)
    if accounts_file is None:
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


def save_accounts(accounts, path="reporter_config/accounts.txt"):
    """Save accounts list back to accounts.txt. Accounts is list of tuples (api_id, api_hash, phone, password)"""
    acct_file = Path(path)
    acct_file.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for api_id, api_hash, phone, password in accounts:
        if password:
            lines.append(f"{api_id},{api_hash},{phone},{password}\n")
        else:
            lines.append(f"{api_id},{api_hash},{phone}\n")
    acct_file.write_text("".join(lines), encoding="utf-8")


def normalize_phone(phone: str) -> str:
    phone = str(phone).strip()
    if phone.startswith("+"):
        return "+" + "".join(ch for ch in phone if ch.isdigit())
    return "".join(ch for ch in phone if ch.isdigit())


def remove_account_by_phone(phone, path="reporter_config/accounts.txt"):
    """Remove account matching phone from accounts.txt and delete its session files."""

    def digits(s):
        return "".join(ch for ch in str(s) if ch.isdigit())

    accounts = load_accounts(path)
    target = digits(phone)
    new_accounts = [a for a in accounts if digits(a[2]) != target]
    if len(new_accounts) == len(accounts):
        return False
    save_accounts(new_accounts, path)

    # delete session files in likely locations (script dir and cwd)
    session_name = sanitize_session_name(phone)
    candidates = [Path(__file__).parent, Path.cwd()]
    for base in candidates:
        for p in base.glob(f"{session_name}*"):
            try:
                if p.is_file():
                    p.unlink()
            except Exception:
                pass
    return True


def append_account(account_tuple, path="reporter_config/accounts.txt"):
    """Append a single account (api_id, api_hash, phone, password) to accounts.txt if not exists."""
    api_id, api_hash, phone, password = account_tuple

    def digits(s):
        return "".join(ch for ch in str(s) if ch.isdigit())

    accounts = load_accounts(path)
    for a in accounts:
        if digits(a[2]) == digits(phone):
            return False

    acct_file = Path(path)
    acct_file.parent.mkdir(parents=True, exist_ok=True)
    line = f"{api_id},{api_hash},{phone}"
    if password:
        line += f",{password}"
    line += "\n"
    with acct_file.open("a", encoding="utf-8") as f:
        f.write(line)
    return True


def load_ban_targets(path="reporter_config/ban.txt"):
    """Load user targets with their report methods from ban.txt"""
    ban_file = find_ban_file(path)
    if ban_file is None:
        print(f"{lrd}[!] ban.txt not found at {path}")
        return {}

    ban_targets = {}
    with ban_file.open("r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue
            if ":" not in raw:
                continue
            parts = raw.split(":")
            if len(parts) != 2:
                continue
            username = parts[0].strip()
            methods_str = parts[1].strip()
            if not username or not methods_str:
                continue

            # Parse methods - can be comma-separated (e.g., "1,3,6") or "all"
            if methods_str.lower() == "all":
                methods = list(REPORT_REASONS.keys())
            else:
                methods = [m.strip() for m in methods_str.split(",")]

            if methods:
                ban_targets[username] = methods
    return ban_targets


def save_ban_targets(ban_targets, path="reporter_config/ban.txt"):
    """Save ban targets back to ban.txt (removes banned accounts)"""
    ban_file = find_ban_file(path)
    if ban_file is None:
        return

    with ban_file.open("w", encoding="utf-8") as f:
        f.write("# Ban.txt - Add user accounts to report automatically\n")
        f.write("# Format: username:method1,method2,method3 OR username:all\n")
        f.write("# Report Methods:\n")
        f.write("# 1 = Report Spam\n")
        f.write("# 2 = Report Other\n")
        f.write("# 3 = Report Violence\n")
        f.write("# 4 = Report Pornography\n")
        f.write("# 5 = Report Copyright\n")
        f.write("# 6 = Report Fake\n")
        f.write("# 7 = Report Geo Irrelevant\n")
        f.write("# 8 = Report Illegal Drugs\n")
        f.write("# 9 = Report Personal Details\n")
        f.write("# 10 = Report Child Abuse\n")
        f.write("#\n")
        f.write("# Examples:\n")
        f.write("# @baduser:1,3,6     (use methods 1, 3, 6)\n")
        f.write("# @fakeuser:all      (use all methods randomly)\n")
        f.write("# Lines starting with # are comments\n\n")

        for username, methods in ban_targets.items():
            if isinstance(methods, list):
                method_str = ",".join(methods)
            else:
                method_str = str(methods)
            f.write(f"{username}:{method_str}\n")


def load_bot_token(path="reporter_config/bot_token.txt"):
    token_file = Path(path)
    if token_file.exists():
        for line in token_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            return stripped
    return None


def save_bot_token(token, path="reporter_config/bot_token.txt"):
    token_file = Path(path)
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(token.strip(), encoding="utf-8")


def get_bot_token(path="reporter_config/bot_token.txt"):
    token = os.environ.get("BOT_TOKEN")
    if token:
        print(f"{lrd}[+] Loaded bot token from BOT_TOKEN environment variable")
        return token.strip()

    token = load_bot_token(path)
    if token:
        print(f"{lrd}[+] Loaded bot token from {path}")
        return token

    token = input(
        f"{lrd}[{lgn}+{lrd}] {gn}Enter Telegram bot token to receive usernames (or leave blank to skip): {k}"
    ).strip()
    if token:
        save_bot_token(token, path)
        return token
    return None


def send_bot_message(bot_token, chat_id, text):
    try:
        payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        urllib.request.urlopen(request, timeout=10, context=context)
        return True
    except Exception:
        return False


def fetch_bot_updates(bot_token, offset=None, timeout=30):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates?timeout={timeout}"
        if offset is not None:
            url += f"&offset={offset}"
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, timeout=timeout + 15, context=context) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            return data.get("result", [])
    except Exception as exc:
        print(f"{lrd}[!] Bot update fetch failed: {exc}")
        return []


def clean_username(text):
    if not text:
        return None
    parts = text.strip().split()
    token = parts[0]
    if token.lower().startswith("/add"):
        if len(parts) < 2:
            return None
        token = parts[1]
    token = token.strip()
    if not token:
        return None
    # Support t.me / telegram.me links and plain usernames
    if "t.me/" in token.lower() or "telegram.me/" in token.lower():
        token = token.split("/")[-1]
        token = token.split("?")[0]
    if token.startswith("@"):
        return token
    return f"@{token}"


def start_bot_listener(bot_token, ban_file_path="reporter_config/ban.txt"):
    if not bot_token:
        return None

    def listener():
        print(f"{lrd}[+] Bot listener started. Send usernames to your bot now.")
        offset = None
        while True:
            updates = fetch_bot_updates(bot_token, offset=offset, timeout=30)
            for update in updates:
                offset = update.get("update_id", 0) + 1
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "")
                if not text or chat_id is None:
                    continue

                # Detect account lines first: api_id,api_hash,phone[,password]
                account_text = text.strip()
                if (
                    account_text.lower().startswith("/addaccount")
                    or account_text.lower().startswith("/add ")
                    or "," in account_text
                ):
                    # If message is /addaccount or plain CSV line, append to accounts.txt
                    if account_text.lower().startswith("/addaccount"):
                        parts = account_text.split(None, 1)
                        account_text = parts[1].strip() if len(parts) > 1 else ""
                    elif account_text.lower().startswith("/add "):
                        parts = account_text.split(None, 1)
                        account_text = parts[1].strip() if len(parts) > 1 else ""

                    parts = [p.strip() for p in account_text.split(",")]
                    if len(parts) < 3 or not parts[0].isdigit():
                        # Not a valid account line, fall back to username handling
                        account_text = None
                    else:
                        api_id = parts[0]
                        api_hash = parts[1]
                        phone = normalize_phone(parts[2])
                        password = parts[3] if len(parts) > 3 else ""
                        added = append_account(
                            (api_id, api_hash, phone, password),
                            "reporter_config/accounts.txt",
                        )
                        if added:
                            send_bot_message(
                                bot_token,
                                chat_id,
                                f"Added account {phone} to accounts.txt",
                            )
                        else:
                            send_bot_message(
                                bot_token,
                                chat_id,
                                f"Account {phone} already exists in accounts.txt",
                            )
                        continue

                username = clean_username(text)
                if not username:
                    send_bot_message(
                        bot_token,
                        chat_id,
                        "Send a username like @username or username to add it to ban.txt.",
                    )
                    continue

                added = append_ban_target(username, "all", ban_file_path)
                if added:
                    send_bot_message(
                        bot_token, chat_id, f"Added {username} to ban.txt."
                    )
                else:
                    send_bot_message(
                        bot_token,
                        chat_id,
                        f"{username} was already in ban.txt or could not be added.",
                    )
            time.sleep(1)

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()
    return thread


def start_bot_account_listener(
    bot_token, accounts_file_path="reporter_config/accounts.txt"
):
    """Start a bot listener that accepts messages with account lines to append to accounts.txt.
    Expected message format: api_id,api_hash,phone[,password]
    Also supports commands like /addaccount api_id,api_hash,phone,password"""
    if not bot_token:
        return None

    def listener():
        print(
            f"{lrd}[+] Account-bot listener started. Send account lines to your bot now."
        )
        offset = None
        while True:
            updates = fetch_bot_updates(bot_token, offset=offset, timeout=30)
            for update in updates:
                offset = update.get("update_id", 0) + 1
                message = update.get("message") or update.get("edited_message")
                if not message:
                    continue
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = (message.get("text") or "").strip()
                if not text or chat_id is None:
                    continue

                # Accept formats: "/addaccount 123,hash,+1234,password" or just the csv line
                token = text
                if token.lower().startswith("/addaccount") or token.lower().startswith(
                    "/add"
                ):
                    parts = token.split(None, 1)
                    if len(parts) < 2:
                        send_bot_message(
                            bot_token,
                            chat_id,
                            "Usage: /addaccount api_id,api_hash,phone[,password]",
                        )
                        continue
                    token = parts[1].strip()

                if "," not in token:
                    send_bot_message(
                        bot_token,
                        chat_id,
                        "Send account as: api_id,api_hash,phone[,password]",
                    )
                    continue

                parts = [p.strip() for p in token.split(",")]
                if len(parts) < 3:
                    send_bot_message(
                        bot_token,
                        chat_id,
                        "Invalid format. Need at least api_id,api_hash,phone",
                    )
                    continue

                api_id = parts[0]
                api_hash = parts[1]
                phone = parts[2]
                password = parts[3] if len(parts) > 3 else ""

                try:
                    int(api_id)
                except Exception:
                    send_bot_message(
                        bot_token, chat_id, "Invalid api_id; must be numeric."
                    )
                    continue

                added = append_account(
                    (api_id, api_hash, phone, password), accounts_file_path
                )
                if added:
                    send_bot_message(
                        bot_token, chat_id, f"Added account {phone} to accounts.txt"
                    )
                else:
                    send_bot_message(
                        bot_token,
                        chat_id,
                        f"Account {phone} already exists in accounts.txt",
                    )

            time.sleep(1)

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()
    return thread


def append_ban_target(username, methods="all", path="reporter_config/ban.txt"):
    ban_file = find_ban_file(path)
    if ban_file is None:
        return False

    username = username.strip()
    if not username:
        return False
    if not username.startswith("@"):
        username = f"@{username}"

    existing = load_ban_targets(path)
    if username in existing:
        print(f"{lrd}[!] {username} already exists in ban.txt")
        return False

    if isinstance(methods, list):
        methods = ",".join([m.strip() for m in methods if m.strip()])
    else:
        methods = str(methods).strip() or "all"

    with ban_file.open("a+", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(f.tell() - 1)
            last_char = f.read(1)
            if last_char != "\n":
                f.write("\n")
        f.write(f"{username}:{methods}\n")

    print(f"{lrd}[+] Added {username} to ban.txt with methods {methods}")
    return True


def sanitize_session_name(phone_number: str) -> str:
    cleaned = "".join(ch for ch in phone_number if ch.isdigit())
    return f"session_{cleaned or 'default'}"


REPORT_REASONS = {
    "1": (types.InputReportReasonSpam, "This channel contains spam content."),
    "2": (types.InputReportReasonOther, "This channel violates Telegram rules."),
    "3": (types.InputReportReasonViolence, "This channel contains violent content."),
    "4": (types.InputReportReasonPornography, "This channel has pornographic content."),
    "5": (types.InputReportReasonCopyright, "This channel violates copyright."),
    "6": (types.InputReportReasonFake, "This channel is impersonating or scamming."),
    "7": (
        types.InputReportReasonGeoIrrelevant,
        "This channel is irrelevant to my region.",
    ),
    "8": (types.InputReportReasonIllegalDrugs, "This channel promotes illegal drugs."),
    "9": (
        types.InputReportReasonPersonalDetails,
        "This channel shares personal details.",
    ),
    "10": (
        getattr(types, "InputReportReasonChildAbuse", types.InputReportReasonOther),
        "This channel contains child abuse content.",
    ),
}


class TelegramReporter:
    def __init__(self):
        # Load accounts from accounts.txt
        self.accounts = load_accounts("reporter_config/accounts.txt")
        if not self.accounts:
            print(f"{lrd}[!] accounts.txt not found or contains no valid accounts.")
            sys.exit(1)

        # Load ban targets from ban.txt
        self.ban_targets = load_ban_targets()
        if not self.ban_targets:
            print(f"{lrd}[!] No ban targets found in ban.txt.")
            sys.exit(1)

        print(f"{lrd}[+] Loaded {len(self.accounts)} account(s)")
        print(f"{lrd}[+] Loaded {len(self.ban_targets)} ban target(s)")

        # Get common password if needed
        self.common_password = ""
        if any(not acc[3] for acc in self.accounts):
            self.common_password = input(
                f"{lrd}[{lgn}+{lrd}] {gn}Enter common two-step password for accounts (leave blank if none): {g}"
            ).strip()

        # Delay between reports (for rate limiting)
        delay_input = input(
            f"{lrd}[{lgn}+{lrd}] {gn}Delay between reports in seconds (default 2): {k}"
        ).strip()
        try:
            self.delay = float(delay_input) if delay_input else 2.0
        except Exception:
            self.delay = 2.0

        # Option to run accounts in parallel
        parallel_input = (
            input(
                f"{lrd}[{lgn}+{lrd}] {gn}Run accounts in parallel? (y/n, default n): {k}"
            )
            .strip()
            .lower()
        )
        self.parallel_accounts = parallel_input in ("y", "yes")

    def report_channel(self):
        """Run continuous reports for all ban targets"""
        self._prepare_accounts()
        if not self.accounts:
            print(f"{lrd}[!] No valid accounts available after preparation.")
            return

        clear()
        re(account)
        print(f"{lrd}[+] Starting continuous user reporting...")
        print(f"{lrd}[+] Loaded {len(self.ban_targets)} user target(s) to report")
        print(
            f"{lrd}[*] Reports will continue until accounts are banned or users removed from ban.txt"
        )
        print(f"{lrd}[*] Press Ctrl+C to stop\n")

        run_count = 0
        try:
            while True:
                run_count += 1
                print(f"{lrd}\n{'='*60}")
                print(
                    f"{lrd}[*] Report cycle #{run_count} - {len(self.ban_targets)} active user(s)"
                )
                print(f"{lrd}{'='*60}")

                # Reload user targets from ban.txt every cycle (checks for bot additions/removals)
                updated_targets = load_ban_targets()
                self.ban_targets = updated_targets

                if not self.ban_targets:
                    print(f"{lrd}[!] No users remaining in ban.txt. Exiting...")
                    break

                # Process each user target
                for user_username, methods_list in list(self.ban_targets.items()):
                    if not self._report_target(user_username, methods_list):
                        # Account was banned, remove from targets
                        print(
                            f"{lrd}[!] Removing {user_username} from ban.txt due to ban/freeze"
                        )
                        del self.ban_targets[user_username]
                        save_ban_targets(self.ban_targets)

                    time.sleep(0.5)  # Small delay between targets

                print(
                    f"{lrd}[*] Cycle #{run_count} completed. Waiting before next cycle..."
                )
                time.sleep(5)  # Delay between cycles

        except KeyboardInterrupt:
            print(f"{lrd}\n[!] User interrupted. Exiting...")

    def _report_target(self, user_username, methods_list):
        """Report a single user target for all accounts using random methods. Returns False if account is banned"""
        if not methods_list:
            print(f"{lrd}[!] No methods available for {user_username}")
            return True  # Continue with other targets

        # Pick a random method for this cycle
        method = random.choice(methods_list)

        if method not in REPORT_REASONS:
            print(f"{lrd}[!] Invalid method {method} for {user_username}")
            return True  # Continue with other targets

        reason_class, default_message = REPORT_REASONS[method]
        message = default_message

        # For "Report Other" method, use default message
        if method == "2":
            message = "This user violates Telegram rules."

        reports_sent = 0
        for api_id, api_hash, phone_number, password in self.accounts:
            result = self._send_report_for_account(
                api_id,
                api_hash,
                phone_number,
                password,
                user_username,
                reason_class,
                message,
            )

            if result == "banned":
                return False  # Signal that account/reporting account is banned
            elif result == "success":
                reports_sent += 1

            time.sleep(self.delay)

        if reports_sent > 0:
            print(
                f"{lrd}[{lgn}+{lrd}] {gn}Sent {reports_sent} report(s) against {user_username} (Method: {method})"
            )

        return True

    def _send_report_for_account(
        self,
        api_id,
        api_hash,
        phone_number,
        password,
        user_username,
        reason_class,
        message,
    ):
        """Send a single user report. Returns 'success', 'failed', or 'banned'"""
        session_name = sanitize_session_name(phone_number)
        try:
            api_id_value = int(api_id)
        except ValueError:
            print(f"{lrd}[!] Invalid api_id for account {phone_number}")
            return "failed"

        try:
            with TelegramClient(session_name, api_id_value, api_hash) as client:
                if not client.is_user_authorized():
                    print(f"{lrd}[!] Account {phone_number} is not authorized")
                    return "failed"

                try:
                    target_peer = client.get_input_entity(user_username)
                except Exception as exc:
                    print(
                        f"{lrd}[!] Could not resolve user {user_username} from {phone_number}: {exc}"
                    )
                    return "failed"

                try:
                    report_reason = reason_class()
                    result = client(
                        functions.account.ReportPeerRequest(
                            peer=target_peer,
                            reason=report_reason,
                            message=message,
                        )
                    )
                    print(
                        f"{lrd}[{lgn}+{lrd}] Report sent: {phone_number} → user {user_username}"
                    )
                    return "success"
                except Exception as exc:
                    error_msg = str(exc).lower()
                    # Check if account is banned/frozen
                    if (
                        "banned" in error_msg
                        or "freeze" in error_msg
                        or "suspended" in error_msg
                    ):
                        print(
                            f"{lrd}[!] Account {phone_number} appears to be banned: {exc}"
                        )
                        # Remove from accounts.txt and delete session files
                        removed = remove_account_by_phone(
                            phone_number, "reporter_config/accounts.txt"
                        )
                        if removed:
                            print(
                                f"{lrd}[+] Removed {phone_number} from accounts.txt and cleaned sessions"
                            )
                        else:
                            print(
                                f"{lrd}[!] Failed to remove {phone_number} from accounts.txt"
                            )
                        return "banned"
                    elif "flood" in error_msg:
                        print(f"{lrd}[!] Rate limited on {phone_number}. Waiting...")
                        time.sleep(10)
                        return "failed"
                    else:
                        print(f"{lrd}[!] Report failed from {phone_number}: {exc}")
                        return "failed"
        except Exception as exc:
            print(f"{lrd}[!] Connection error for {phone_number}: {exc}")
            return "failed"

    def _prepare_accounts(self):
        prepared = []
        for api_id, api_hash, phone_number, password in self.accounts:
            session_name = sanitize_session_name(phone_number)
            try:
                api_id_value = int(api_id)
            except ValueError:
                print(f"{lrd}Invalid api_id for account {phone_number}.")
                continue

            client = None
            try:
                client = TelegramClient(session_name, api_id_value, api_hash)
                client.connect()
                print(f"{lrd}[{lgn}+{lrd}] Connected to {phone_number}")
                if not client.is_user_authorized():
                    print(f"{lrd}[!] Preparing account {phone_number}")
                    client.send_code_request(phone_number)
                    code = input(
                        f"{lrd}Enter login code for {phone_number}: {g}"
                    ).strip()
                    try:
                        client.sign_in(phone_number, code)
                    except SessionPasswordNeededError:
                        account_password = password or self.common_password
                        if account_password:
                            client.sign_in(password=account_password)
                        else:
                            pwd = input(
                                f"{lrd}Two-step password required for {phone_number}. Enter password: {g}"
                            ).strip()
                            client.sign_in(password=pwd)
                prepared.append((api_id, api_hash, phone_number, password))
            except SessionPasswordNeededError:
                account_password = password or self.common_password
                if account_password:
                    client.sign_in(password=account_password)
                    prepared.append((api_id, api_hash, phone_number, password))
                else:
                    pwd = input(
                        f"{lrd}Two-step password required for {phone_number}. Enter password: {g}"
                    ).strip()
                    client.sign_in(password=pwd)
                    prepared.append((api_id, api_hash, phone_number, password))
            except Exception as exc:
                print(f"{lrd}[!] Account {phone_number} failed to prepare: {exc}")
            finally:
                if client is not None:
                    try:
                        if client.is_connected():
                            client.disconnect()
                            print(f"{lrd}[{lgn}+{lrd}] Disconnected {phone_number}")
                    except Exception:
                        pass

        self.accounts = prepared


if __name__ == "__main__":
    bot_token = get_bot_token()
    if bot_token:
        start_bot_listener(bot_token)

    reporter = TelegramReporter()
    reporter.report_channel()
