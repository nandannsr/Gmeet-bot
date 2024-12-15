from pydantic import BaseModel

class MeetJoinerConfig(BaseModel):
    meeting_url: str
    video_url: str
    audio_url: str


class AudioRecorderConfig(BaseModel):
    output_file: str = "output.wav"