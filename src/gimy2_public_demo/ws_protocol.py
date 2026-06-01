import base64
import hashlib
import json
import os
import socket
import struct
from dataclasses import dataclass


GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xA


class WebSocketProtocolError(RuntimeError):
    pass


def _read_exact(sock, size):
    chunks = []
    remaining = size
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise WebSocketProtocolError("connection closed while reading")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _read_http_headers(sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise WebSocketProtocolError("connection closed during handshake")
        data += chunk
        if len(data) > 65536:
            raise WebSocketProtocolError("handshake headers too large")
    header_text = data.split(b"\r\n\r\n", 1)[0].decode("iso-8859-1")
    lines = header_text.split("\r\n")
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()
    return lines[0], headers


def accept_handshake(sock):
    request_line, headers = _read_http_headers(sock)
    if not request_line.startswith("GET "):
        raise WebSocketProtocolError("expected GET websocket handshake")
    key = headers.get("sec-websocket-key")
    if not key:
        raise WebSocketProtocolError("missing Sec-WebSocket-Key")
    accept = base64.b64encode(hashlib.sha1((key + GUID).encode("ascii")).digest()).decode("ascii")
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n"
        "\r\n"
    )
    sock.sendall(response.encode("ascii"))
    return request_line, headers


def client_handshake(sock, host, port, path="/"):
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    headers = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}:{port}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {key}",
        "Sec-WebSocket-Version: 13",
    ]
    sock.sendall(("\r\n".join(headers) + "\r\n\r\n").encode("ascii"))
    status_line, response_headers = _read_http_headers(sock)
    if not status_line.startswith("HTTP/1.1 101"):
        raise WebSocketProtocolError(f"websocket handshake failed: {status_line}")
    expected = base64.b64encode(hashlib.sha1((key + GUID).encode("ascii")).digest()).decode("ascii")
    if response_headers.get("sec-websocket-accept") != expected:
        raise WebSocketProtocolError("invalid Sec-WebSocket-Accept")


def _apply_mask(payload, mask_key):
    return bytes(byte ^ mask_key[index % 4] for index, byte in enumerate(payload))


def send_frame(sock, opcode, payload=b"", mask=False):
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    first = 0x80 | opcode
    length = len(payload)
    if length < 126:
        header = struct.pack("!BB", first, (0x80 if mask else 0) | length)
    elif length < (1 << 16):
        header = struct.pack("!BBH", first, (0x80 if mask else 0) | 126, length)
    else:
        header = struct.pack("!BBQ", first, (0x80 if mask else 0) | 127, length)
    if mask:
        mask_key = os.urandom(4)
        sock.sendall(header + mask_key + _apply_mask(payload, mask_key))
    else:
        sock.sendall(header + payload)


def recv_frame(sock):
    first, second = struct.unpack("!BB", _read_exact(sock, 2))
    fin = bool(first & 0x80)
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    if not fin:
        raise WebSocketProtocolError("fragmented frames are not supported in this demo")
    if length == 126:
        length = struct.unpack("!H", _read_exact(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(sock, 8))[0]
    mask_key = _read_exact(sock, 4) if masked else None
    payload = _read_exact(sock, length) if length else b""
    return opcode, _apply_mask(payload, mask_key) if mask_key else payload


@dataclass
class WebSocketConnection:
    sock: socket.socket
    mask_outgoing: bool = False

    def send_json(self, payload):
        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        send_frame(self.sock, OPCODE_TEXT, text, mask=self.mask_outgoing)

    def send_binary(self, payload):
        send_frame(self.sock, OPCODE_BINARY, payload, mask=self.mask_outgoing)

    def recv_json(self):
        opcode, payload = self._recv_data_frame()
        if opcode != OPCODE_TEXT:
            raise WebSocketProtocolError(f"expected text frame, got opcode {opcode}")
        return json.loads(payload.decode("utf-8"))

    def recv_binary(self):
        opcode, payload = self._recv_data_frame()
        if opcode != OPCODE_BINARY:
            raise WebSocketProtocolError(f"expected binary frame, got opcode {opcode}")
        return payload

    def close(self):
        try:
            send_frame(self.sock, OPCODE_CLOSE, b"", mask=self.mask_outgoing)
        finally:
            self.sock.close()

    def _recv_data_frame(self):
        while True:
            opcode, payload = recv_frame(self.sock)
            if opcode == OPCODE_PING:
                send_frame(self.sock, OPCODE_PONG, payload, mask=self.mask_outgoing)
                continue
            if opcode == OPCODE_PONG:
                continue
            if opcode == OPCODE_CLOSE:
                raise WebSocketProtocolError("websocket closed")
            return opcode, payload


class WebSocketClient(WebSocketConnection):
    @classmethod
    def connect(cls, host, port, path="/", timeout=5):
        sock = socket.create_connection((host, port), timeout=timeout)
        try:
            client_handshake(sock, host, port, path)
        except Exception:
            sock.close()
            raise
        return cls(sock=sock, mask_outgoing=True)

