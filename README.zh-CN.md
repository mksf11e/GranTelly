# GIMY

面向老人和异地家人的 AI 亲情沟通桥梁。

GIMY ,GranTelly项目的核心，也是一组亲情沟通 agent 的名字。它帮助老人通过简单的设备分享生活，也帮助异地家人收到简洁的近况摘要、上下文和话题建议。

这个公开仓库是为 **UCWS Singapore Hackathon 2026** 准备的**脱敏可运行 demo 骨架**。它展示系统架构、设备协议和本地 mock 流程，但不包含私人 prompt、真实家庭记忆、密钥、部署细节或生产数据。

老人端交互非常简单：不用 App、不用打字，只需要“看、按、说”，就能通过一台会说话的适老化小电视分享自己的生活，也理解家人发来的内容。GIMY 不是替代亲密关系中的责任，而是一个低干扰的桥梁，促进家人更自然、更定期地沟通。

## 这个 demo 展示什么

- ESP32 风格的 WebSocket 设备协议。
- transcript / reply 的 JSON 文本消息。
- 通过 WebSocket binary frame 向设备推送 JPEG 图片。
- 简化版“老人问照片”流程。
- 本地 mock ESP32 客户端。
- 显示图片预处理管线。

## 不包含什么

- 真实 OpenClaw agent prompt 或私人记忆。
- 真实家庭对话记录或摘要。
- Telegram bot token、chat id、配对数据或 allowlist。
- 模型 provider token、VPS 地址、gateway token 或部署 secret。
- 生产环境 vector memory 或 plugin 数据。

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.gimy2_public_demo.demo_server
```

另开一个终端：

```bash
python -m src.gimy2_public_demo.mock_esp32_ws --text "这是什么照片？"
```

## 说明

电子纸屏幕指的是类似墨水屏的低功耗显示屏，适合长时间展示照片。公开 demo 中的模型接口统一描述为 `OpenAI-compatible multimodal model endpoint`，不会公开真实 provider 配置。
