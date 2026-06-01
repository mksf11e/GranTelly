# Tech Stack

## Product Summary

GIMY, short for **Grandma I Miss You**, is a dual-agent family communication bridge for older adults and remote families. Gimy is also the name of the agent experience: it helps the elder share daily life through a simple talking device, while helping family members receive summaries, context, and conversation prompts.

The elder-side product is designed as an elder-friendly little TV: no app, no typing, just look, press, and speak. GIMY is a low-friction bridge for more regular family communication, not a replacement for human care or relationship responsibility.

## Hardware

- ESP32-S3-class embedded device.
- One press-and-hold recording button.
- Microphone and speaker path handled on the device side.
- 7.3-inch color e-paper display for low-power photo presentation.
- Wi-Fi connection to a WebSocket device bridge.

## Device Protocol

- ESP32 connects as a WebSocket client.
- The backend acts as the WebSocket server.
- Transcript and reply events are JSON text frames.
- Display images are sent as raw JPEG binary frames.
- The conversation flow and image push flow are intentionally independent.

## Backend

- Python demo bridge for public protocol simulation.
- Private deployment uses OpenClaw-based agent orchestration and structured memory.
- Family-side interface uses a Telegram bot during demo stage.
- Multimodal understanding is abstracted as an OpenAI-compatible multimodal model endpoint.

## Image Pipeline

- Receive a family photo.
- Enhance or normalize it for display.
- Resize and center-crop to the display target.
- Rotate for the final hardware orientation.
- Push the prepared JPEG to the connected device.

## Privacy Boundary

- Public repo stores only sample metadata and mock data.
- Real family memory, prompts, sessions, photos, tokens, chat IDs, and deployment state are excluded.
