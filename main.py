import json
import time
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

topics = {}
active_users = {}

def get_unique_username(topic, username):
    if topic not in topics or username not in topics[topic]:
        return username
    num = 2
    new_name = f"{username}#{num}"
    while new_name in topics[topic]:
        num += 1
        new_name = f"{username}#{num}"
    return new_name

async def broadcast(topic, message, sender_ws):
    for user, ws in topics[topic].items():
        if ws != sender_ws:
            try:
                await ws.send_text(json.dumps(message))
            except:
                pass

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()

    try:
        initial_text = await websocket.receive_text()
        try:
            initial_data = json.loads(initial_text)
            username = initial_data["username"]
            topic = initial_data["topic"]
        except:
            await websocket.send_text("Invalid join format")
            await websocket.close()
            return

        if topic not in topics:
            topics[topic] = {}

        username = get_unique_username(topic, username)

        topics[topic][username] = websocket
        active_users[websocket] = (username, topic)

        print(f"{username} joined {topic}")

        while True:
            try:
                text = await websocket.receive_text()
            except WebSocketDisconnect:
                break

            if text == "/list":
                response = "Active Topics:\n"
                for t, users in topics.items():
                    response += f"{t} ({len(users)} users)\n"
                await websocket.send_text(response.strip())
                continue

            msg = {
                "username": username,
                "message": text,
                "timestamp": int(time.time())
            }

            await broadcast(topic, msg, websocket)
            await websocket.send_text(json.dumps({"status": "delivered"}))

            asyncio.create_task(asyncio.sleep(30))

    finally:
        if websocket in active_users:
            username, topic = active_users[websocket]
            print(f"{username} left {topic}")

            del active_users[websocket]
            if username in topics.get(topic, {}):
                del topics[topic][username]

            if topic in topics and len(topics[topic]) == 0:
                del topics[topic]
                print(f"Removed empty topic: {topic}")
