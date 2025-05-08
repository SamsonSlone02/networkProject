import asyncio
import websockets
from datetime import datetime, timedelta

#Store last_seen times by IP or device ID
last_seen = {}

async def handler(websocket):
    client_ip = websocket.remote_address[0]
    print(f"Connected: {client_ip}")

    try:
        async for message in websocket:
            now = datetime.utcnow()

            if message == "heartbeat":
                last_seen[client_ip] = now
                print(f"Heartbeat from {client_ip} at {now.isoformat()}")
            else:
                print(f"Message from {client_ip}: {message}")
                last_seen[client_ip] = now
                await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print(f"Disconnected: {client_ip}")
    except Exception as e:
        print(f"Error with {client_ip}: {e}")

async def monitor_devices():
    while True:
        await asyncio.sleep(10)
        print("\nDevice Status Report:")
        now = datetime.utcnow()
        for client_ip, seen_time in last_seen.items():
            online = (now - seen_time) < timedelta(seconds=15)
            status = "ONLINE" if online else "OFFLINE"
            print(f"  {client_ip} - Last seen: {seen_time.isoformat()} - {status}")
        print("")

async def main():
    print("Starting WebSocket server on 0.0.0.0:8000")
    server = websockets.serve(handler, "0.0.0.0", 8000)
    await asyncio.gather(server, monitor_devices())

asyncio.run(main())
