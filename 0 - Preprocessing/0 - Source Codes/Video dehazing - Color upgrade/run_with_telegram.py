import os
import sys
import time
import json
import argparse
import urllib.request

# Add script directory to path so main.py functions can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from main import verify_cuda, process_video_pipeline

DEFAULT_BOT_TOKEN = "8895091102:AAH4zBelYvfzto2UXiLJrZIzJvolKt9k2OY"
DEFAULT_INPUT_DIR = r"C:\Users\parsa\Desktop\New folder"
DEFAULT_OUTPUT_DIR = r"C:\Users\parsa\Desktop\New folder\dehazed"

def fetch_telegram_chat_id(bot_token):
    """Queries Telegram getUpdates API to automatically find the latest chat_id."""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("ok") and data.get("result"):
                for update in reversed(data["result"]):
                    if "message" in update and "chat" in update["message"]:
                        return update["message"]["chat"]["id"]
                    elif "edited_message" in update and "chat" in update["edited_message"]:
                        return update["edited_message"]["chat"]["id"]
    except Exception as e:
        print(f"[Telegram Warning] Failed to reach Telegram API: {e}")
    return None

def resolve_chat_id(bot_token):
    """Resolves chat_id automatically or waits for user to send a Telegram message."""
    print(f"\n[Telegram Setup] Checking for active chat session with bot...")
    chat_id = fetch_telegram_chat_id(bot_token)
    if chat_id:
        print(f"[Telegram Setup] Active Chat ID found: {chat_id}")
        return chat_id

    print("\n" + "=" * 70)
    print("  TELEGRAM ACTION REQUIRED:")
    print("  Please open your Telegram app and send a message (e.g. '/start' or 'Hello')")
    print("  to your Telegram Bot so it knows where to send notifications.")
    print("=" * 70 + "\n")

    print("Waiting for Telegram message...", end="", flush=True)
    for _ in range(15):
        time.sleep(2)
        print(".", end="", flush=True)
        chat_id = fetch_telegram_chat_id(bot_token)
        if chat_id:
            print(f"\n[Telegram Setup] Connected! Chat ID: {chat_id}")
            return chat_id

    print("\n[Telegram Notice] Could not detect automatic chat ID.")
    user_input = input("Enter your Telegram Chat ID manually (or press Enter to skip Telegram alerts): ").strip()
    return user_input if user_input else None

def send_telegram_notification(bot_token, chat_id, text):
    """Sends a Telegram message using Markdown formatting."""
    if not bot_token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Telegram Error] Failed to send message: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Dehazing Runner with Telegram Progress Notifications")
    parser.add_argument("--input", "-i", type=str, default=DEFAULT_INPUT_DIR, help="Path to input video folder")
    parser.add_argument("--output", "-o", type=str, default=DEFAULT_OUTPUT_DIR, help="Path to output video folder")
    parser.add_argument("--token", "-t", type=str, default=DEFAULT_BOT_TOKEN, help="Telegram Bot API Token")
    parser.add_argument("--scale", type=str, default="0.5", help="Inference scale factor")
    parser.add_argument("--fp16", action="store_true", default=True, help="Use FP16 precision")
    parser.add_argument("--dehaze", action="store_true", default=True, help="Apply MSRCR dehazing pre-processing")
    args = parser.parse_args()

    verify_cuda()

    input_dir = os.path.abspath(args.input.strip("'\""))
    output_dir = os.path.abspath(args.output.strip("'\""))
    bot_token = args.token.strip()

    if not os.path.exists(input_dir):
        print(f"[ERROR] Input directory does not exist: '{input_dir}'")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Setup Telegram Chat ID
    chat_id = resolve_chat_id(bot_token)

    # Scan for video files excluding output directory
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm')
    video_files = []
    
    for root, _, files in os.walk(input_dir):
        # Exclude output_dir from scanning if inside input_dir
        if os.path.commonpath([output_dir, root]) == output_dir:
            continue
        for file in files:
            if file.lower().endswith(video_extensions) and not file.endswith("_temp.mp4"):
                video_files.append(os.path.join(root, file))

        video_files = sorted(list(set(video_files)))

    if not video_files:
        msg = f"⚠️ *No videos found* to process in `{input_dir}`."
        print(f"[INFO] {msg}")
        send_telegram_notification(bot_token, chat_id, msg)
        return

    start_msg = (
        f"🚀 *Dehazing Pipeline Started*\n\n"
        f"📂 *Input Directory:* `{input_dir}`\n"
        f"📁 *Output Directory:* `{output_dir}`\n"
        f"🎬 *Total Videos Found:* `{len(video_files)}`"
    )
    print("\n" + "=" * 75)
    print(start_msg.replace("*", "").replace("`", ""))
    print("=" * 75)
    send_telegram_notification(bot_token, chat_id, start_msg)

    successful_count = 0
    failed_count = 0
    total_count = len(video_files)

    for idx, vid_path in enumerate(video_files, 1):
        filename = os.path.basename(vid_path)
        rel_path = os.path.relpath(vid_path, input_dir)
        target_out = os.path.join(output_dir, rel_path)

        vid_start_msg = f"🎬 *[{idx}/{total_count}] Processing Video:* `{filename}`"
        print(f"\n({idx}/{total_count}) Starting: {filename}")
        send_telegram_notification(bot_token, chat_id, vid_start_msg)

        start_time = time.time()
        success = process_video_pipeline(vid_path, target_out, script_dir, scale=args.scale, fp16=args.fp16, dehaze=args.dehaze)
        elapsed = time.time() - start_time
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s" if elapsed >= 60 else f"{elapsed:.1f}s"

        if success:
            successful_count += 1
            vid_done_msg = f"✅ *[{idx}/{total_count}] Finished:* `{filename}`\n⏱️ *Time:* `{elapsed_str}`"
            send_telegram_notification(bot_token, chat_id, vid_done_msg)
        else:
            failed_count += 1
            vid_fail_msg = f"❌ *[{idx}/{total_count}] Failed:* `{filename}`"
            send_telegram_notification(bot_token, chat_id, vid_fail_msg)

    end_msg = (
        f"🎉 *Dehazing Pipeline Finished!*\n\n"
        f"✅ *Successfully Processed:* `{successful_count}/{total_count}`\n"
        f"❌ *Failures:* `{failed_count}`\n"
        f"📁 *Saved To:* `{output_dir}`"
    )
    print("\n" + "=" * 75)
    print(end_msg.replace("*", "").replace("`", ""))
    print("=" * 75)
    send_telegram_notification(bot_token, chat_id, end_msg)

if __name__ == "__main__":
    main()
