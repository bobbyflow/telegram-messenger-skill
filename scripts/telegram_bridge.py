import win32gui
import win32con
import win32api
import time
import sys
import os
import subprocess
import uiautomation as auto
import pyperclip

# Telegram Desktop Path
TELEGRAM_PATH = os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe")

def ensure_telegram_open():
    hwnd = win32gui.FindWindow("Qt5152QWindowIcon", None)
    if not hwnd:
        hwnd = win32gui.FindWindow(None, "Telegram")
    
    if hwnd and win32gui.IsWindowVisible(hwnd):
        return hwnd
    
    print("Telegram is hidden or closed. Attempting to launch/wake...")
    if os.path.exists(TELEGRAM_PATH):
        subprocess.Popen([TELEGRAM_PATH])
        for _ in range(20):
            time.sleep(1)
            hwnd = win32gui.FindWindow("Qt5152QWindowIcon", None)
            if not hwnd:
                hwnd = win32gui.FindWindow(None, "Telegram")
            if hwnd and win32gui.IsWindowVisible(hwnd):
                print("Telegram window is now visible.")
                time.sleep(1)
                return hwnd
    return hwnd

def atomic_paste(with_enter=False):
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl down
    win32api.keybd_event(0x56, 0, 0, 0) # V down
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0) # V up
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0) # Ctrl up
    if with_enter:
        time.sleep(0.1)
        win32api.keybd_event(0x0D, 0, 0, 0) # Enter down
        win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0) # Enter up

def raw_clear():
    # Ctrl+A then Backspace
    win32api.keybd_event(0x11, 0, 0, 0)
    win32api.keybd_event(0x41, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(0x08, 0, 0, 0)
    win32api.keybd_event(0x08, 0, win32con.KEYEVENTF_KEYUP, 0)

def verify_chat_header(win_ctrl, contact):
    try:
        # Telegram headers are usually TextControls in the title bar area
        win_rect = win_ctrl.BoundingRectangle
        top_boundary = win_rect.top + (win_rect.bottom - win_rect.top) * 0.2
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=15):
            if ctrl.ControlTypeName == "TextControl":
                if ctrl.BoundingRectangle.bottom < top_boundary:
                    if contact.lower() in ctrl.Name.lower():
                        print(f"Identity Verified: Found '{ctrl.Name}' in Telegram header.")
                        return True
    except:
        pass
    return False

def get_target_msg_box(win_ctrl):
    max_area = 0
    target = None
    try:
        win_rect = win_ctrl.BoundingRectangle
        win_height = win_rect.bottom - win_rect.top
        for ctrl, _ in auto.WalkControl(win_ctrl, maxDepth=20):
            if ctrl.ControlTypeName == "EditControl" and "Search" not in ctrl.Name:
                rect = ctrl.BoundingRectangle
                if rect.top > (win_rect.top + win_height * 0.5):
                    area = (rect.right - rect.left) * (rect.bottom - rect.top)
                    if area > max_area:
                        max_area = area
                        target = ctrl
    except:
        pass
    return target

def send_telegram_message(contact, message=None, image_path=None, auto_send=False):
    hwnd = ensure_telegram_open()
    if not hwnd: return False

    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        tg_win = auto.ControlFromHandle(hwnd)
        
        # --- ATOMIC SEARCH ---
        print(f"Searching for Telegram contact: {contact}")
        # Telegram Reset (ESC)
        win32api.keybd_event(0x1B, 0, 0, 0)
        win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
        
        # Search Hotkey (Ctrl+F)
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x46, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(0x46, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.2)
        
        # Paste contact and ENTER
        pyperclip.copy(contact)
        atomic_paste(with_enter=True)
        time.sleep(1.0)
        
        # Follow focus (if popped out)
        active_hwnd = win32gui.GetForegroundWindow()
        target_win = auto.ControlFromHandle(active_hwnd)
        
        # --- DELIVERY ---
        msg_box = get_target_msg_box(target_win)
        if msg_box:
            msg_box.SetFocus()
            time.sleep(0.2)
            
            if image_path and os.path.exists(image_path):
                p_path = image_path.replace("'", "''")
                subprocess.run(["powershell.exe", "-NoProfile", "-Command", f"Set-Clipboard -Path '{p_path}'"])
                time.sleep(1.0)
                atomic_paste(with_enter=False)
                time.sleep(1.5)

            if message:
                pyperclip.copy(message)
                msg_box.SetFocus()
                atomic_paste(with_enter=False)
            
            if auto_send:
                time.sleep(0.5)
                win32api.keybd_event(0x0D, 0, 0, 0)
                win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
                print(f"Successfully SENT to Telegram: {contact}")
            else:
                print(f"DONE: Message pasted for {contact} on Telegram. (Halt mode)")
            return True
        else:
            print("Error: Could not identify Telegram message input area.")
            return False
            
    except Exception as e:
        print(f"Telegram Bridge Error: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("contact")
    parser.add_argument("--message", default=None)
    parser.add_argument("--image", default=None)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    send_telegram_message(args.contact, args.message, args.image, auto_send=args.send)
