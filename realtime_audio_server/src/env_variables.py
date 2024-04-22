from dotenv import load_dotenv
import os
# END IMPORTS

if load_dotenv():
    print('Loading .env variables')

# ENV VARIABLES
ASSEMBLYAI_API_KEY = os.environ.get('ASSEMBLYAI_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID')
