import win32gui
import win32con
import win32api
import win32process
import time
import sys
import os
import subprocess
import uiautomation as auto
import pyperclip
import json
import urllib.request
import ctypes

user32 = ctypes.windll.user32

# --- PORTABLE CONFIGURATION ---
def find_telegram_path():
    possible_paths = [
        os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Telegram Desktop\Telegram.exe"),
        r"C:\Program Files\Telegram Desktop\Telegram.exe",
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Telegram Desktop\\Telegram.exe")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return "Telegram.exe" # Fallback to PATH

TELEGRAM_PATH = find_telegram_path()
# Bot token and Chat ID remain constant for this specific skill deployment
BOT_TOKEN = "8134458002:AAESCHwDz6GD1qw0CCs9zbckEmPtLRwFa8E" 
MY_CHAT_ID = "8232676046"

def block_input(block=True):
    """Freezes hardware input (Keyboard/Mouse). Requires Admin."""
    try:
        user32.BlockInput(block)
    except:
        pass

def set_topmost(hwnd, is_topmost=True):
    """Forces window to absolute Z-order priority (Always on Top)."""
    if not hwnd or not win32gui.IsWindow(hwnd): return
    z_order = win32con.HWND_TOPMOST if is_topmost else win32con.HWND_NOTOPMOST
    win32gui.SetWindowPos(hwnd, z_order, 0, 0, 0, 0, 
                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)

def ensure_telegram_open():
    hwnd = win32gui.FindWindow("Qt5152QWindowIcon", None)
    if not hwnd: hwnd = win32gui.FindWindow(None, "Telegram")
    if hwnd and win32gui.IsWindowVisible(hwnd): return hwnd
    if os.path.exists(TELEGRAM_PATH):
        subprocess.Popen([TELEGRAM_PATH])
        for _ in range(20):
            time.sleep(1)
            hwnd = win32gui.FindWindow("Qt5152QWindowIcon", None)
            if hwnd and win32gui.IsWindowVisible(hwnd): return hwnd
    return hwnd

def atomic_paste(with_enter=False):
    win32api.keybd_event(0x11, 0, 0, 0)
    win32api.keybd_event(0x56, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    if with_enter:
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, 0, 0)
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)

def force_focus(hwnd, fast=False):
    """Hostile Focus: Uses Thread Attachment and Alt-key bypass."""
    if not hwnd or not win32gui.IsWindow(hwnd):
        return False
    try:
        if not fast: win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        foreground_thread_id = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[0]
        current_thread_id = win32api.GetCurrentThreadId()
        if foreground_thread_id != current_thread_id:
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, True)
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32gui.SetForegroundWindow(hwnd)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32process.AttachThreadInput(current_thread_id, foreground_thread_id, False)
        else:
            win32gui.SetForegroundWindow(hwnd)
        iterations = 3 if fast else 15
        for _ in range(iterations):
            if win32gui.GetForegroundWindow() == hwnd:
                if not fast: time.sleep(0.3)
                return True
            time.sleep(0.1 if fast else 0.2)
            win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"Force Focus Error: {e}")
    return False

def send_as_user(contact, message):
    print(f"--- INITIATING AGGRESSIVE TELEGRAM BRIDGE ---")
    hwnd = ensure_telegram_open()
    if not hwnd: return False
    
    block_input(True)
    set_topmost(hwnd, True)
    
    try:
        if not force_focus(hwnd):
            print("ABORT: Could not seize focus.")
            return False
            
        time.sleep(0.8)
        
        # Reset & Search
        win32api.keybd_event(0x1B, 0, 0, 0) # ESC
        win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
        win32api.keybd_event(0x11, 0, 0, 0) # Ctrl+F
        win32api.keybd_event(0x46, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.3)
        
        pyperclip.copy(contact)
        atomic_paste(with_enter=True)
        time.sleep(1.2)
        
        # JIT Focus Re-assertion before message paste
        force_focus(hwnd, fast=True)
        
        # Paste Message
        pyperclip.copy(message)
        atomic_paste(with_enter=False)
        print(f"DONE: Message pasted for {contact} as User.")
        return True
    except Exception as e:
        print(f"User Mode Error: {e}")
        return False
    finally:
        set_topmost(hwnd, False)
        block_input(False)
        print("--- AGGRESSIVE TELEGRAM BRIDGE COMPLETE ---")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("contact")
    parser.add_argument("message")
    parser.add_argument("--mode", choices=["cloud", "user"], default="user")
    args = parser.parse_args()
    
    if args.mode == "user":
        send_as_user(args.contact, args.message)
    else:
        # Default cloud route for now
        print("Sending via Cloud API...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": MY_CHAT_ID, "text": args.message}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            print(json.load(response).get('ok'))
