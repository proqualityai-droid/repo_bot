# Reporter Configuration Guide

## Setup Instructions

### 1. Add Accounts to `accounts.txt`
Format: `api_id,api_hash,phone_number,password`
- `api_id`: Your Telegram API ID
- `api_hash`: Your Telegram API Hash  
- `phone_number`: Phone number associated with the account
- `password`: (Optional) Two-step verification password

Example:
```
12345678,abcdef123456,+1234567890,mypassword
87654321,fedcba654321,+9876543210,
```

### 2. Add Ban Targets to `ban.txt`
Format: `username:method1,method2,method3` OR `username:all`
- `username`: User/account to report (e.g., `@username`)
- `methods`: Comma-separated list of report reasons OR `all` for all methods
- **Har cycle mein randomly ek method pick hoga**

Report Methods:
- **1** = Report Spam
- **2** = Report Other
- **3** = Report Violence
- **4** = Report Pornography
- **5** = Report Copyright
- **6** = Report Fake
- **7** = Report Geo Irrelevant
- **8** = Report Illegal Drugs
- **9** = Report Personal Details
- **10** = Report Child Abuse

Example:
```
@baduser:1,3,6        → Cycle 1: Spam, Cycle 2: Violence, Cycle 3: Fake (random)
@fakeuser:all         → Har cycle mein randomly koi bhi method (1-10)
@troll_user:1,2,3     → In 3 methods mein se random
```

### 3. Run the Reporter
```bash
python reporter.py
```

The script will:
1. Ask for common password (if needed)
2. Ask for report delay in seconds (default 2)
3. Ask to run accounts in parallel (optional)
4. Start continuous reporting

## Features

✅ **Automatic Account Loading** - Reads accounts from `accounts.txt`
✅ **Automatic Target Loading** - Reads ban targets from `ban.txt`
✅ **Continuous Reporting** - Reports run in cycles
✅ **Ban Detection** - Automatically removes banned accounts from reporting
✅ **Multiple Methods** - Different report reasons for different targets
✅ **Rate Limiting** - Configurable delay between reports
✅ **Parallel Processing** - Optional parallel account processing

## How It Works

1. **Initialization**: Loads accounts and ban targets
2. **Validation**: Prepares and validates all accounts
3. **Reporting**: Continuously sends reports in cycles
   - Each cycle processes all targets
   - Each target uses all active accounts
   - Configurable delay between cycles
4. **Ban Detection**: If an account is banned/frozen:
   - It's removed from reporting
   - Username is removed from `ban.txt`
   - Reports continue with remaining accounts
5. **Target Removal**: If a target is manually removed from `ban.txt`:
   - Changes are detected on next cycle
   - Reports stop for that target

## Tips

- Add new ban targets to `ban.txt` while the script is running
- Remove targets by deleting their line from `ban.txt`
- Use lower delay values for aggressive reporting (minimum 1 second)
- Use higher delay values to avoid rate limiting
- Run in parallel mode for faster reporting across multiple accounts
- Keep `accounts.txt` and `ban.txt` in the `reporter_config` folder

## Troubleshooting

- **"accounts.txt not found"** - Make sure `accounts.txt` exists in the same folder as `reporter.py`
- **"No ban targets found"** - Add entries to `ban.txt`
- **Rate limiting errors** - Increase the delay between reports
- **Account not authorized** - Check phone number and password are correct
