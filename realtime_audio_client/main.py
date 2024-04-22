import pygame
import pyaudio
import websockets
import asyncio
import base64
import json
import io


# PLAY AUDIO IN TERMINAL
async def play_audio_bytes(audio_bytes):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(io.BytesIO(audio_bytes))
    sound.play()
    pygame.time.wait(int(sound.get_length() * 1000))


FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

# START THE RECORDING
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

URL = "ws://127.0.0.1:8000/user-audio-input"


async def send_and_receive():
    async with websockets.connect(URL) as websocket:
        await asyncio.sleep(0.1)
        session_begins = await websocket.recv()
        print(session_begins)

        async def send_data():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data": str(data)})
                    await websocket.send(json_data)
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    break
                except Exception as e:
                    stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=FRAMES_PER_BUFFER
                    )
                await asyncio.sleep(0.01)
            return True

        async def receive_data():
            while True:
                try:
                    result = await websocket.recv()
                    data = json.loads(result)
                    if data['type'] == 'transcription':
                        print(data['data'], end=' ', flush=True)
                    if data['type'] == 'gpt':
                        print(data['data'], end=' ', flush=True)
                    if data['type'] == 'voice':
                        audio_bytes = base64.b64decode(data['data'])
                        print("Elevenslab Voice...")
                        await play_audio_bytes(audio_bytes)

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    break
                except Exception as e:
                    assert False, "Not a websocket"

        await asyncio.gather(send_data(), receive_data())


asyncio.run(send_and_receive())
