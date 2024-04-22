# Description
This is a realtime voice and transcription streaming project. It is completely built with the Python3.
User speaks into the mic and the transcription of the speech words is shown on the terminal, the response of the speech is generated from the GPT-3.5 and it is also shown on the user terminal in realtime. The GPT response is converted into the voice using Elevenslab Websocket.
This whole project is made with the websockets. It contains the websocket of FastAPI, AssemblyAI Streaming SDK, OpenAI Streaming SDK, Elevenslab streaming websocket API and client side websocket connection.


# Tools & Technologies Used
1. Python 3.10.12
2. FastAPI (for websocket server)
3. OpenAI (for answer generation)
4. AssemblyAI (for speech to text)
5. Elevenslab (for text to speech)

# Points to remember
- It does not handle multiple users
- Only tested on Linux

# Setup & Installation for Linux
1. Install portaudio package
`sudo apt install portaudio19-dev`
2. Clone the repository
`git clone https://github.com/ahsanumair7/realtime-audio-streaming.git`
3. Create a virtualenv for Python
`pip install virtualenv`
`python3.10 -m virtualenv venv`
4. Activate the virtual environment
`source venv/bin/activate`
5. Install the python libraries via requirements.txt file
`pip install -r requirements.txt`
6. Rename the example.env file into .env which located in realtime_audio_server folder

# Setup & Installation for Windows
1. Clone the repository
`git clone https://github.com/ahsanumair7/realtime-audio-streaming.git`
2. Create a virtualenv for Python
`pip install virtualenv`
`virtualenv venv`
3. Activate the virtual environment
`venv\Scripts\activate`
4. Install the python libraries via requirements.txt file
`pip install -r requirements.txt`
5. Rename the example.env file into .env which located in realtime_audio_server folder

# How to run
1. Run the server. Go inside realtime_audio_server folder. main.py file is the entry point.
`uvicorn main:app` (By default your server would be running at port 8000)
2. Go to the realtime_audio_client folder and run the client in new terminal.
`python main.py`
3. Talk into the mic and you will see the output into client terminal