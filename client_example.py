import asyncio
import websockets
import json

async def client():
    ws = await websockets.connect("ws://localhost:8000/ws")

    join_data = {"username": "user1", "topic": "sports"}
    await ws.send(json.dumps(join_data))
    print("Joined topic:", join_data["topic"])

    await ws.send("Hello everyone!")
    print("Sent message")

    for i in range(5):
        msg = await ws.recv()
        print("Received:", msg)

asyncio.run(client())
