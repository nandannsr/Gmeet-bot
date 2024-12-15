# main.py

# from bot.meet_joiner import join_google_meet
from dotenv import load_dotenv

load_dotenv()
from bot.meet_joiner_v2 import GoogleMeetBot
from config import MEETING_URL, VIDEO_URL, AUDIO_PATH
from bot.utils import print_welcome_message
from bot.models import MeetJoinerConfig


if __name__ == "__main__":
    # Load configuration
    # Start WebSocket in a separate thread
    config = MeetJoinerConfig(
        meeting_url=MEETING_URL, video_url=VIDEO_URL, audio_url=AUDIO_PATH
    )

    # Print welcome message
    print_welcome_message()

    # Start the process of joining the Google Meet and recording audio
    bot = GoogleMeetBot(config)
    bot.join_meeting()
