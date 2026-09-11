import base64
import json
from io import BytesIO
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
import httpx
from PIL import Image

app = FastAPI()
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234" 

def convert_webp_to_jpeg(b64_string: str) -> str:
    image_data = base64.b64decode(b64_string)
    image = Image.open(BytesIO(image_data)).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    target_url = f"{LM_STUDIO_BASE_URL}/{path}"
    body = await request.body()
    
    if request.method == "POST" and path.endswith("v1/chat/completions"):
        try:
            data = json.loads(body)
            modified = False
            if "messages" in data:
                for message in data["messages"]:
                    if isinstance(message.get("content"), list):
                        for item in message["content"]:
                            if item.get("type") == "image_url":
                                url = item["image_url"]["url"]
                                if url.startswith("data:image/webp;base64,"):
                                    b64_data = url.split(",", 1)[1]
                                    new_b64 = convert_webp_to_jpeg(b64_data)
                                    item["image_url"]["url"] = f"data:image/jpeg;base64,{new_b64}"
                                    modified = True
            if modified:
                body = json.dumps(data).encode('utf-8')
        except Exception as e:
            print(f"Ошибка парсинга JSON: {e}")

    req_headers = dict(request.headers)
    req_headers.pop("host", None)
    req_headers.pop("content-length", None)

    # Отключаем таймаут ожидания (timeout=None), чтобы модель могла генерировать ответ любой длительности
    client = httpx.AsyncClient(timeout=None)
    
    req = client.build_request(
        method=request.method,
        url=target_url,
        headers=req_headers,
        content=body,
        params=request.query_params
    )
    
    response = await client.send(req, stream=True)
    
    res_headers = dict(response.headers)
    res_headers.pop("content-encoding", None)
    res_headers.pop("content-length", None)

    async def stream_generator():
        try:
            async for chunk in response.aiter_raw():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    return StreamingResponse(
        stream_generator(),
        status_code=response.status_code,
        headers=res_headers
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5444)