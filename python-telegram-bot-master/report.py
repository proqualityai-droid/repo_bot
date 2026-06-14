import os
import time

try:
    from telethon.sync import TelegramClient
    from telethon import errors
except ImportError:
    os.system("pip install telethon")
    from telethon.sync import TelegramClient
    from telethon import errors
from telethon.tl import types
from telethon import functions


from pathlib import Path


def load_accounts(path="accounts.txt"):
    candidate_paths = [
        Path(path),
        Path(__file__).parent / path,
        Path(__file__).parent.parent / path,
    ]

    accounts_file = None
    for candidate in candidate_paths:
        if candidate.exists():
            accounts_file = candidate
            break

    if accounts_file is None:
        raise FileNotFoundError(
            "Accounts file not found. Create a file named accounts.txt with lines in this format:\n"
            "api_id,api_hash,phone,password\n"
            "Common locations checked:\n"
            f"  - {candidate_paths[0]}\n"
            f"  - {candidate_paths[1]}\n"
            f"  - {candidate_paths[2]}"
        )

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


def get_session_name(phone: str) -> str:
    cleaned_phone = "".join(ch for ch in phone if ch.isdigit())
    if not cleaned_phone:
        cleaned_phone = "default"
    return f"reporter_{cleaned_phone}"


def delete_session_file(session_name: str):
    for suffix in [".session", ".session-journal"]:
        path = Path(f"{session_name}{suffix}")
        if path.exists():
            path.unlink()


def report_with_account(
    api_id, api_hash, phone, password, target_username, report_count
):
    session_name = get_session_name(phone)
    print(f"\n=== Using account {phone} (session={session_name}) ===")

    try:
        api_id_value = int(api_id)
    except ValueError:
        print("api_id must be a number.")
        return False

    client = TelegramClient(session_name, api_id_value, api_hash)
    auth_key_error = getattr(errors, "AuthKeyError", None)

    try:
        client.connect()

        if not client.is_user_authorized():
            try:
                client.start(phone=phone, password=password)
            except Exception as exc:
                message = str(exc).lower()
                if auth_key_error and isinstance(exc, auth_key_error):
                    message = "authkeyerror"

                if "authkeyerror" in message or "invalid new nonce hash" in message:
                    print("Broken session file or auth-key mismatch detected.")
                    client.disconnect()
                    delete_session_file(session_name)
                    client = TelegramClient(session_name, api_id_value, api_hash)
                    client.connect()
                    try:
                        client.start(phone=phone, password=password)
                    except Exception as exc2:
                        print(f"Retry login failed: {exc2}")
                        return False
                elif isinstance(exc, errors.rpcerrorlist.ApiIdInvalidError):
                    print("Invalid api_id/api_hash for this account.")
                    return False
                elif isinstance(exc, errors.rpcerrorlist.PhoneNumberInvalidError):
                    print("Invalid phone number for this account.")
                    return False
                elif isinstance(exc, errors.rpcerrorlist.PhoneCodeInvalidError):
                    print("Invalid login code or code expired.")
                    return False
                else:
                    print(f"Login failed: {exc}")
                    return False

        try:
            target = client.get_entity(target_username)
        except ValueError:
            print(f"Target not found: {target_username}")
            return False
        except errors.rpcerrorlist.UsernameNotOccupiedError:
            print(f"Target username is not occupied: {target_username}")
            return False
        except Exception as exc:
            print(f"Could not resolve target: {exc}")
            return False

        try:
            peer = types.InputPeerUser(
                user_id=target.id,
                access_hash=target.access_hash,
            )
        except AttributeError:
            print("Target entity is not a reportable user.")
            return False

        for i in range(1, report_count + 1):
            try:
                client(
                    functions.account.ReportPeerRequest(
                        peer=peer,
                        reason=types.InputReportReasonChildAbuse(),
                        message="This user is suspected of child abuse.",
                    )
                )
                print(f"[{i}/{report_count}] report sent from {phone}")
                time.sleep(1)
            except Exception as exc:
                print(f"Failed to send report #{i} from {phone}: {exc}")
                return False

    finally:
        client.disconnect()

    return True


def main():
    print("Multi-account auto report sender")
    print("Prepare accounts.txt with lines: api_id,api_hash,phone,password")
    print("If password is not required, leave it empty after the last comma.")

    target_username = input("Enter target username or ID: ").strip()
    if not target_username:
        print("Target username is required.")
        return

    report_count = input("Enter number of reports per account: ").strip()
    if not report_count.isdigit() or int(report_count) <= 0:
        print("Report count must be a positive number.")
        return
    report_count = int(report_count)

    try:
        accounts = load_accounts()
    except FileNotFoundError as exc:
        print(exc)
        return

    if not accounts:
        print("No valid accounts found in accounts.txt.")
        return

    for api_id, api_hash, phone, password in accounts:
        report_with_account(
            api_id, api_hash, phone, password, target_username, report_count
        )

    print("\nAll done.")


if __name__ == "__main__":
    main()
