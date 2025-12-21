import requests
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext

SOLANA_RPC = "https://api.mainnet-beta.solana.com"
RENT_EXEMPT_LAMPORTS = 2039280  # ~0.00203928 SOL

def get_token_accounts(wallet):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    r = requests.post(SOLANA_RPC, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()["result"]["value"]

def scan_empty_accounts(wallet):
    accounts = get_token_accounts(wallet)
    empty_accounts = []
    total_lamports = 0
    for acc in accounts:
        info = acc["account"]["data"]["parsed"]["info"]
        token_amount = int(info["tokenAmount"]["amount"])
        if token_amount == 0:
            lamports = acc["account"]["lamports"]
            empty_accounts.append({
                "address": acc["pubkey"],
                "lamports": lamports
            })
            total_lamports += lamports
    return empty_accounts, total_lamports

def lamports_to_sol(lamports):
    return lamports / 1_000_000_000

# --- GUI ---

def run_scan():
    wallet = wallet_entry.get().strip()
    if not wallet or len(wallet) < 32:
        messagebox.showerror("Error", "Enter a valid Solana wallet address.")
        return
    scan_btn.config(state="disabled")
    result_box.delete(1.0, tk.END)
    try:
        empty_accounts, total_lamports = scan_empty_accounts(wallet)
        if not empty_accounts:
            result_box.insert(tk.END, "No empty token accounts found.\n")
        else:
            result_box.insert(tk.END, f"Found {len(empty_accounts)} empty token accounts:\n\n")
            for acc in empty_accounts:
                result_box.insert(tk.END, f"{acc['address']} | {lamports_to_sol(acc['lamports']):.6f} SOL\n")
            result_box.insert(tk.END, f"\nTotal reclaimable SOL: {lamports_to_sol(total_lamports):.6f}\n")
            result_box.insert(tk.END, "\nTo reclaim: Use a wallet (e.g. Solflare) to close these accounts.")
    except Exception as e:
        result_box.insert(tk.END, f"Error: {e}\n")
    scan_btn.config(state="normal")

root = tk.Tk()
root.title("Solana Rent Reclaimer")
root.geometry("600x400")
tk.Label(root, text="Paste your Solana wallet address:").pack(pady=8)
wallet_entry = tk.Entry(root, width=60)
wallet_entry.pack()
scan_btn = tk.Button(root, text="Scan for Empty Token Accounts", command=run_scan)
scan_btn.pack(pady=8)
result_box = scrolledtext.ScrolledText(root, width=70, height=18)
result_box.pack(padx=8, pady=8)
tk.Label(root, text="No keys required. Non-custodial.").pack(pady=2)
root.mainloop()
