---
name: telegram-messenger
description: Send results and images to your local Telegram Desktop account via a surgical Python bridge. Use when you need to output data to Telegram contacts or groups without UI interference.
---

# Telegram Messenger

This skill allows AI agents to send text output and images directly to your local Telegram Desktop client using a hardware-resilient Python bridge.

## ðŸŒŸ Key Features
- **âš¡ Atomic Delivery**: Uses high-speed clipboard injection to bypass physical keyboard interference.
- **ðŸ› ï¸ Self-Healing**: Automatically launches Telegram if it's closed or hidden in the system tray.
- **ðŸ›¡ï¸ Absolute Zero Aggression**: Forces Telegram to front and locks hardware input (Requires Admin).

## Tools

### send_to_telegram
Sends a message or image to a specific Telegram contact.

- **Arguments**:
  - `contact`: The name of the contact or group.
  - `message` (optional): The text to send.
  - `image` (optional): The absolute local path to an image file.
  - `send` (optional): Set to true to actually transmit (default: false / Halt mode).

- **Command**:
  `python "%USERPROFILE%\.gemini\skills\telegram-messenger\scripts\telegram_bridge.py" "<contact>" "<message>"`

## Workflow
1.  Identify the target contact and content.
2.  Use the `send_to_telegram` command to deliver.
3.  By default, the script stays in **Halt Mode** (pastes but doesn't send). Include `--send` for full automation.

## Constraints
- **Telegram Desktop Required**: The Windows Desktop application must be installed.

---
Bobby Choi, Sovereign | Opal, Architect
