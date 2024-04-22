from fastapi import WebSocket, APIRouter
from .env_variables import (
    ASSEMBLYAI_API_KEY,
    OPENAI_API_KEY,
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID
)
import openai
import websockets
import asyncio
import base64
import json
import io
import assemblyai as aai
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
import audioop
# END IMPORTS


audio_router = APIRouter()  # ROUTER INITIATION

# SDKs Initialization
openai.api_key = OPENAI_API_KEY
aai.settings.api_key = ASSEMBLYAI_API_KEY

websocket_conn = None


def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session:", session_opened)


def on_data(transcript: aai.RealtimeTranscript):

    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        asyncio.run(render_transcription('\r\n'+transcript.text+'\r\n'))
        messages = [{'role': 'system', 'content': 'You are an AI based agent. Help the user.'}, {
            'role': 'user', 'content': transcript.text}]
        asyncio.run(chat_completion(messages))

    else:
        asyncio.run(render_transcription(transcript.text))


def on_error(error: aai.RealtimeError):
    print("An error occured:", error)


def on_close():
    print("Closing Session")


transcriber = aai.RealtimeTranscriber(
    on_data=on_data,
    on_error=on_error,
    sample_rate=16_000,
    on_open=on_open,
    on_close=on_close,
)

transcriber.connect()


# ROUTES
@audio_router.websocket('/user-audio-input')
async def user_audio_input(websocket: WebSocket):
    global websocket_conn

    await websocket.accept()
    websocket_conn = websocket

    await websocket.send_text("Connected with server..")

    while True:
        data = await websocket.receive_text()
        audio_bytes = base64.b64decode(json.loads(data)["audio_data"])
        transcriber.stream(audio_bytes)


async def render_transcription(text):
    await asyncio.sleep(0.01)
    global websocket_conn
    print('Render Transcription..')
    data = json.dumps({"type": "transcription", "data": str(text)})
    await websocket_conn.send_text(data)


async def chat_completion(messages):
    global websocket_conn
    print('Inside chat completion..')

    response = await openai.ChatCompletion.acreate(model='gpt-3.5-turbo', messages=messages, temperature=0.5, stream=True,
                                                   max_tokens=250)

    async def text_iterator():
        full_resp = []
        async for chunk in response:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                content = delta['content']
                print(content, end=' ', flush=True)
                data = json.dumps({"type": "gpt", "data": str(content)})
                await websocket_conn.send_text(data)
                full_resp.append(content)
                yield content
            else:
                print('<end of gpt response>')
                break
    await text_to_speach_streaming(text_iterator(), websocket_conn)


async def text_chunker(chunks):  # SPLIT TEXT FOR ELEVENS LAB
    """Split text into chunks, ensuring to not break sentences."""
    splitters = ('.', ',', '?', '!', ';', ':', '—',
                 '-', '(', ')', '[', ']', '}', ' ')
    buffer = ''

    async for text in chunks:
        if buffer.endswith(splitters):
            yield buffer + ' '
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + ' '
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + ' '


# CONVERT ELEVENSLAB AUDIO INTO TELEPHONIC FORMAT & SEND TO TWILIO SOCKET
async def stream(audio_stream, user_socket):
    async for chunk in audio_stream:
        if chunk:
            try:
                audio = AudioSegment.from_file(
                    io.BytesIO(chunk), format='mp3')
                if audio.channels == 2:
                    audio = audio.set_channels(1)
                resampled = audioop.ratecv(
                    audio.raw_data, 2, 1, audio.frame_rate, 8000, None)[0]
                audio_segment = AudioSegment(
                    data=resampled, sample_width=audio.sample_width, frame_rate=8000, channels=1)
                pcm_audio = audio_segment.export(format='wav')
                pcm_data = pcm_audio.read()
                encoded_audio = base64.b64encode(pcm_data).decode('utf-8')
                try:
                    json_data = json.dumps(
                        {"type": "voice", "data": str(encoded_audio)})
                    await user_socket.send_text(json_data)
                    print("Voice sent to user..")
                except websockets.exceptions.ConnectionClosedError:
                    user_socket.close()
            except (CouldntDecodeError, IndexError):
                pass


async def text_to_speach_streaming(text_iterator, user_socket):
    uri = f'wss://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream-input?model_id=eleven_monolingual_v1&optimize_streaming_latency=4'
    async with websockets.connect(uri) as elevenslab_socket:
        await elevenslab_socket.send(json.dumps({'text': ' ', 'voice_settings': {'stability': 1, 'similarity_boost': True},
                                                 'xi_api_key': ELEVENLABS_API_KEY, }))

        async def listen():
            while True:
                try:
                    message = await elevenslab_socket.recv()
                    data = json.loads(message)
                    if data.get('audio'):
                        yield base64.b64decode(data['audio'])
                    elif data.get('isFinal'):
                        break
                except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError) as e:
                    await elevenslab_socket.close()
                    print(e)
                    break

        listen_task = asyncio.create_task(stream(listen(), user_socket))

        async for text in text_chunker(text_iterator):
            await elevenslab_socket.send(json.dumps({'text': text, 'try_trigger_generation': True}))
        await elevenslab_socket.send(json.dumps({'text': ''}))

        await listen_task
