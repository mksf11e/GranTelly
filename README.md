# GIMY

AI-powered family connection for older adults and remote families.

GIMY, short for **Grandma I Miss You**, is a dual-agent family communication bridge. Gimy is also the name of the agent experience: it helps older adults share daily life through a simple elder-side device, while helping remote family members receive concise updates, context, and conversation prompts.

This public repository is a **sanitized runnable demo skeleton** for UCWS Singapore Hackathon 2026. It shows the architecture, protocol, and local mock flow without exposing private prompts, real family memory, credentials, deployment details, or production data.

The elder-side interaction is intentionally simple: no app, no typing, just look, press, and speak through a talking elder-friendly little TV. GIMY is not a replacement for family responsibility; it is a low-friction bridge that encourages more regular and natural communication.

## What This Demo Shows

- ESP32-style WebSocket device protocol.
- JSON transcript and reply messages.
- Binary JPEG image push to a connected device.
- A simplified photo question flow.
- A local mock ESP32 client.
- A display image preparation pipeline.

## What Is Not Included

- Real OpenClaw agent prompts or private memory.
- Real family conversation history or summaries.
- Real Telegram bot credentials, chat IDs, pairing data, or allowlists.
- Real provider tokens, VPS addresses, gateway tokens, or deployment secrets.
- Production vector memory or plugin data.

## Architecture

```text
Family Telegram Bot
        |
        v
Photo / text ingestion
        |
        v
Agent orchestration + structured memory
        |
        v
WebSocket device bridge  <---->  ESP32-S3 elder device
        |
        v
Color e-paper display + speaker
```

The public code uses a local mock server instead of the private production stack. The real system uses an OpenAI-compatible multimodal model endpoint and OpenClaw-based agent orchestration.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.gimy2_public_demo.demo_server
```

In another terminal:

```bash
python -m src.gimy2_public_demo.mock_esp32_ws --text "What is this photo?"
```

Optional image preparation:

```bash
python -m src.gimy2_public_demo.photo_pipeline --input path/to/your-photo.jpg --output runtime/display.jpg
```

## Protocol

The ESP32 connects as a WebSocket client to:

```text
ws://localhost:8765/device
```

Text frames are JSON. Image frames are raw JPEG bytes.

See [docs/esp32-websocket-protocol.md](docs/esp32-websocket-protocol.md).

## Documentation

- [Tech stack](docs/tech-stack.md)
- [Architecture](docs/architecture.md)
- [ESP32 WebSocket protocol](docs/esp32-websocket-protocol.md)
- [Public release notes](docs/public-release-notes.md)

## License

Copyright (c) 2026.

This public demo is shared for hackathon review and collaboration discussion. No open-source license is granted unless a separate license is added later.
