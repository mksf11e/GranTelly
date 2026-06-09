# Architecture

## Overview

GIMY, the GranTelly, is built as a bridge between two familiar interaction modes:

- The elder speaks naturally to a simple physical device.
- The family member uses a normal chat interface.

Gimy is also the name of the agent experience. The system turns family photos into conversation starters, helps the elder share daily life, and turns the response into concise family updates and conversation context.

## Main Components

```text
Family chat channel
        |
        v
Photo ingestion + metadata
        |
        v
Agent orchestration + structured memory
        |
        v
WebSocket device bridge
        |
        v
ESP32 elder device
```

## Runtime Flow

1. A family member sends a photo.
2. The backend stores image metadata and prepares a display-ready image.
3. The backend pushes a JPEG binary frame to the connected device.
4. The elder asks about the photo by voice.
5. The device sends ASR text as a transcript event.
6. The backend returns a short TTS-ready reply.
7. After the elder answers a follow-up question, the family side receives a concise summary.

## Public Demo Simplification

The public skeleton replaces private production services with local mock behavior:

- No real Telegram polling.
- No real provider keys.
- No private OpenClaw prompts.
- No real memory database.
- No personal family context.

This keeps the repository safe for public review while preserving the core technical shape.
