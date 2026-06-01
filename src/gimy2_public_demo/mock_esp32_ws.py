import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from .ws_protocol import WebSocketClient


def run_mock(url, text, device_id, save_photo=None, timeout=10):
    parsed = urlparse(url)
    if parsed.scheme != "ws":
        raise ValueError("public mock supports ws:// URLs")
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80
    path = parsed.path or "/device"

    client = WebSocketClient.connect(host, port, path, timeout=timeout)
    try:
        client.send_json({"type": "hello", "device_id": device_id})
        hello_ack = client.recv_json()
        print(json.dumps(hello_ack, ensure_ascii=False))

        client.send_json(
            {
                "type": "transcript",
                "session_id": hello_ack["session_id"],
                "device_id": device_id,
                "text": text,
            }
        )
        reply = client.recv_json()
        print(json.dumps(reply, ensure_ascii=False))

        if save_photo:
            client.send_json({"type": "push_current_photo", "session_id": hello_ack["session_id"]})
            ack = client.recv_json()
            payload = client.recv_binary()
            output = Path(save_photo)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
            print(json.dumps(ack, ensure_ascii=False))
            print(f"saved_photo={output}")
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Mock ESP32 WebSocket client for the public GIMY demo.")
    parser.add_argument("--url", default="ws://127.0.0.1:8765/device")
    parser.add_argument("--text", default="What is this photo?")
    parser.add_argument("--device-id", default="esp32-public-demo")
    parser.add_argument("--save-photo", default=None)
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()
    run_mock(args.url, args.text, args.device_id, save_photo=args.save_photo, timeout=args.timeout)


if __name__ == "__main__":
    main()
