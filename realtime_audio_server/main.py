from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import audio_router
from src.constants import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION
)
# END IMPORTS


# APP CONFIG
app = FastAPI(title=API_TITLE, description=API_DESCRIPTION,
              version=API_VERSION)

origins = ['127.0.0.1', 'localhost']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_router)
