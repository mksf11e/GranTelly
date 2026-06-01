import argparse
import json
import socketserver
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .ws_protocol import WebSocketConnection, WebSocketProtocolError, accept_handshake


SAMPLE_PHOTO_ID = "sample-photo-001"
SAMPLE_JPEG_BYTES = b"\xff\xd8" + b"GIMY public demo JPEG placeholder" + b"\xff\xd9"


class DemoServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler_class, runtime_dir):
        super().__init__(server_address, handler_class)
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.device_connections = {}
        self.lock = threading.Lock()
        self.demo_state = "ready"

    def register(self, conn, send_lock, device_id):
        key = id(conn)
        with self.lock:
            self.device_connections[key] = (conn, send_lock, device_id)
        return key

    def unregister(self, key):
        with self.lock:
            self.device_connections.pop(key, None)

    def push_photo(self, payload=SAMPLE_JPEG_BYTES):
        with self.lock:
            connections = list(self.device_connections.values())
        pushed = 0
        for conn, send_lock, _device_id in connections:
            try:
                with send_lock:
                    conn.send_binary(payload)
                pushed += 1
            except OSError:
                pass
        return pushed


class DemoHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.send_lock = threading.Lock()
        self.connection_key = None
        try:
            accept_handshake(self.request)
            conn = WebSocketConnection(self.request, mask_outgoing=False)
            self.connection_key = self.server.register(conn, self.send_lock, "unknown-device")
            session_id = f"demo-{uuid.uuid4().hex[:10]}"
            while True:
                message = conn.recv_json()
                self.handle_message(conn, session_id, message)
        except (ConnectionError, OSError, WebSocketProtocolError):
            return
        finally:
            self.server.unregister(self.connection_key)

    def handle_message(self, conn, session_id, message):
        message_type = message.get("type")
        if message_type == "hello":
            self.reply(
                conn,
                {
                    "type": "hello_ack",
                    "session_id": session_id,
                    "server_time": datetime.now(timezone.utc).isoformat(),
                },
            )
            return
        if message_type == "push_current_photo":
            self.reply(
                conn,
                {
                    "type": "push_photo_ack",
                    "session_id": message.get("session_id", session_id),
                    "pushed": len(self.server.device_connections),
                    "byte_length": len(SAMPLE_JPEG_BYTES),
                },
            )
            self.server.push_photo()
            return
        if message_type == "transcript":
            self.reply(conn, build_demo_reply(self.server, message, session_id))
            return
        self.reply(
            conn,
            {
                "type": "error",
                "session_id": message.get("session_id", session_id),
                "error": f"unsupported message type: {message_type}",
            },
        )

    def reply(self, conn, payload):
        with self.send_lock:
            conn.send_json(payload)


def build_demo_reply(server, message, fallback_session_id):
    text = (message.get("text") or "").strip()
    session_id = message.get("session_id") or fallback_session_id
    if server.demo_state == "ready" and looks_like_photo_question(text):
        server.demo_state = "awaiting_status"
        return {
            "type": "reply",
            "session_id": session_id,
            "text": "This is a family photo shared for you. How has your day been?",
            "emotion": "warm",
            "current_photo_id": SAMPLE_PHOTO_ID,
        }
    if server.demo_state == "awaiting_status":
        server.demo_state = "complete"
        summary = render_demo_summary(text)
        (server.runtime_dir / "demo-last-summary.md").write_text(summary, encoding="utf-8")
        return {
            "type": "reply",
            "session_id": session_id,
            "text": "I wrote that down and prepared a family update.",
            "emotion": "warm",
            "current_photo_id": SAMPLE_PHOTO_ID,
        }
    return {
        "type": "reply",
        "session_id": session_id,
        "text": "I am here with you. Please take your time and tell me more.",
        "emotion": "calm",
        "current_photo_id": SAMPLE_PHOTO_ID,
    }


def looks_like_photo_question(text):
    lowered = text.lower()
    return any(token in lowered for token in ("photo", "picture", "image", "what is this", "what's this"))


def render_demo_summary(elder_reply):
    return (
        "# Demo Family Update\n\n"
        "- The elder asked about the latest photo.\n"
        f"- The elder replied: {elder_reply or 'No additional status provided.'}\n"
        "- This is mock output for the public demo skeleton.\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Run the sanitized GIMY public demo WebSocket server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--runtime-dir", default="runtime")
    args = parser.parse_args()

    server = DemoServer((args.host, args.port), DemoHandler, runtime_dir=args.runtime_dir)
    print(f"GIMY public demo server listening on ws://{args.host}:{args.port}/device")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
