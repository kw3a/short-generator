import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
    
    @property
    def TIKTOK_SESSIONID(self) -> str:
        return os.getenv("TIKTOK_SESSIONID", "")

    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def CLIENT_ID(self) -> str:
        return os.getenv("CLIENT_ID", "")

    @property
    def CLIENT_SECRET(self) -> str:
        return os.getenv("CLIENT_SECRET", "")

    @property
    def USER_AGENT(self) -> str:
        return os.getenv("USER_AGENT", "")

    @property
    def SUBREDDIT(self) -> str:
        return "stories"

    @property
    def VOICE(self) -> str:
        return "nova"

    @property
    def AUDIO_FILE(self) -> str:
        return "output.mp3"

    @property
    def VIDEO_FILE(self) -> str:
        return "satisfying.mp4"

    @property
    def TEXT_FILE(self) -> str:
        return "text.txt"

    @property
    def METADATA_FILE(self) -> str:
        return "metadata.json"

    @property
    def OUTPUT_FILE(self) -> str:
        return "short.mp4"

    @property
    def CLIP_FILE(self) -> str:
        return "clip.mp4"

    @property
    def OUTPUT_DIR(self) -> str:
        return "workspace"

    @property
    def CONTENT_DIR(self) -> str:
        return "content"

    @property
    def ELEVENLABS_API_KEY(self) -> str:
        return os.getenv("ELEVENLABS_API_KEY", "")

    @property
    def AZURE_KEY(self) -> str:
        return os.getenv("AZURE_KEY", "")

    @property
    def AZURE_REGION(self) -> str:
        return os.getenv("AZURE_REGION", "")
    
    @property
    def LANGUAGES(self) -> list[str]:
        return ["spanish", "english"]  

config = Config()
