---
name: telegram-messenger
description: Send results and images to your local Telegram Desktop account via a surgical Python bridge. Use when you need to output data to Telegram contacts or groups without UI interference.
---

# Telegram Messenger

This skill allows AI agents to send text output and images directly to your local Telegram Desktop client using a hardware-resilient Python bridge.

## 🌟 Key Features
- **⚡ Atomic Delivery**: Uses high-speed clipboard injection to bypass physical keyboard interference.
- **🛠️ Self-Healing**: Automatically launches Telegram if it's closed or hidden in the system tray.
- **🔄 Follow-the-Focus**: Automatically detects and re-binds if a chat is in a standalone window.

## Tools

### send_to_telegram
Sends a message or image to a specific Telegram contact.

- **Arguments**:
  - `contact`: The name of the contact or group.
  - `message` (optional): The text to send.
  - `image` (optional): The absolute local path to an image file.
  - `send` (optional): Set to true to actually transmit (default: false / Halt mode).

- **Command**:
  `python C:\Users\choib\.gemini\skills	elegram-messenger\scripts	elegram_bridge.py "<contact>" [--message "<message>"] [--image "<image_path>"] [--send]`

## Workflow
1.  Identify the target contact and content.
2.  Use the `send_to_telegram` command to deliver.
3.  By default, the script stays in **Halt Mode** (pastes but doesn't send). Include `--send` for full automation.

## Constraints
- **Telegram Desktop Required**: The Windows Desktop application must be installed.

---
Engineered by Opal | Systems Architect
