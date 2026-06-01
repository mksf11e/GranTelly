# GIMY

面向長者和異地家人的 AI 親情溝通橋樑。

GIMY 是 **Grandma I Miss You** 的縮寫，也是一組親情溝通 agent 的名字。它幫助長者透過簡單設備分享生活，也幫助異地家人收到簡潔的近況摘要、上下文和話題建議。

這個公開倉庫是為 **UCWS Singapore Hackathon 2026** 準備的**脫敏可運行 demo 骨架**。它展示系統架構、設備協議和本地 mock 流程，但不包含私人 prompt、真實家庭記憶、金鑰、部署細節或生產資料。

長者端互動非常簡單：不用 App、不用打字，只需要「看、按、說」，就能透過一台會說話的適老化小電視分享自己的生活，也理解家人傳來的內容。GIMY 不是替代親密關係中的責任，而是一個低干擾的橋樑，促進家人更自然、更定期地溝通。

## 這個 demo 展示什麼

- ESP32 風格的 WebSocket 設備協議。
- transcript / reply 的 JSON 文字訊息。
- 透過 WebSocket binary frame 向設備推送 JPEG 圖片。
- 簡化版「長者問照片」流程。
- 本地 mock ESP32 client。
- 顯示圖片預處理管線。

## 不包含什麼

- 真實 OpenClaw agent prompt 或私人記憶。
- 真實家庭對話紀錄或摘要。
- Telegram bot token、chat id、配對資料或 allowlist。
- 模型 provider token、VPS 位址、gateway token 或部署 secret。
- 生產環境 vector memory 或 plugin 資料。

## 快速開始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.gimy2_public_demo.demo_server
```

另開一個終端：

```bash
python -m src.gimy2_public_demo.mock_esp32_ws --text "這是什麼照片？"
```

## 說明

電子紙螢幕指的是類似墨水屏的低功耗顯示屏，適合長時間展示照片。公開 demo 中的模型接口統一描述為 `OpenAI-compatible multimodal model endpoint`，不公開真實 provider 配置。
