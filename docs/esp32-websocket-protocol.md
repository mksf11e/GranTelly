# ESP32 WebSocket Protocol

## Endpoint

```text
ws://localhost:8765/device
```

In production, this URL is provided by the deployment environment. The public repo uses localhost only.

## Frame Types

- JSON text frames for control, transcript, and reply messages.
- JPEG binary frames for display image updates.

## Device Hello

Device to server:

```json
{
  "type": "hello",
  "device_id": "esp32-public-demo"
}
```

Server to device:

```json
{
  "type": "hello_ack",
  "session_id": "demo-session-id",
  "server_time": "2026-06-01T00:00:00Z"
}
```

## Transcript

Device to server:

```json
{
  "type": "transcript",
  "session_id": "demo-session-id",
  "device_id": "esp32-public-demo",
  "text": "What is this photo?"
}
```

Server to device:

```json
{
  "type": "reply",
  "session_id": "demo-session-id",
  "text": "This looks like a family photo shared for you. How has your day been?",
  "emotion": "warm",
  "current_photo_id": "sample-photo-001"
}
```

## Independent Photo Push

The server may send a raw JPEG binary frame at any time. It does not need to be attached to a transcript response.

Expected display image:

- JPEG format.
- 800 x 480 target size in this public demo.
- Prepared by the backend before sending.

## Design Principle

Conversation and photo refresh are separate:

- Transcript in, reply out.
- Image push happens only when the backend decides the display should update.

