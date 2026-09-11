# 🔄 DSH to LM Studio WebP Proxy

A simple yet effective local proxy server built with **FastAPI** to solve image format compatibility issues between **dsh** and local vision models in **LM Studio**.

## ⚠️ The Problem
By default, the **dsh** tool optimizes and encodes all attached images into the `webp` format before sending them. However, most Vision models running in **LM Studio** do not support `webp` and expect a standard `jpeg` or `png` file. Because of this, sending an image usually results in a parsing error or a flat-out rejection by the model.

## 💡 How It Works
The `proxy.py` script acts as a transparent middleware:
1. It intercepts requests sent from dsh to LM Studio.
2. It scans for images formatted as `data:image/webp;base64` within the `POST` request body (specifically targeting the `/v1/chat/completions` endpoint).
3. It unpacks the image in memory, converts it to `JPEG` on the fly using Pillow, and reconstructs the JSON payload.
4. It transparently forwards the modified request to LM Studio and streams the model's response back to dsh.

---

## 🚀 Installation & Usage

### Option 1: Quick Start (Windows)
The project includes a `.bat` script that automates the entire setup process:
1. Make sure **Python** is installed on your system.
2. Run the provided `run_proxy.bat` file.
3. The script will automatically create an isolated `.venv` virtual environment, install the required dependencies (`fastapi`, `uvicorn`, `pillow`, `httpx`), and launch the server.

### Option 2: Manual Setup (Linux / macOS / Windows)
If you prefer setting up the environment manually via the terminal:

```bash
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate it
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn pillow httpx

# 4. Run the proxy server
python proxy.py
```

Once running, the server will be available at: `http://127.0.0.1:5444`

---

## ⚙️ Configuring dsh

To route your traffic through the converter, you need to change the target API URL in your **dsh** configuration.

Instead of the default LM Studio address (`http://127.0.0.1:1234`), specify the local address of the running proxy:
* **API Base URL / Endpoint:** `http://127.0.0.1:5444`

*(If dsh requires the full path to the API, use `http://127.0.0.1:5444/v1`).*

You're all set! Now, all images sent from dsh will be properly intercepted, converted to JPEG, and successfully processed by your local models in LM Studio.
