import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bot.models import MeetJoinerConfig
from media_players.media_stream import VirtualMediaStreamer
from bot.audio_recorder import AudioRecorder
from openai_voice_assistant.realtime_voice_bot import AudioWebSocketClient
import os

API_KEY = os.environ.get("OPEN_API_KEY")
WS_URL = os.environ.get("OPEN_WS_URL")


class GoogleMeetBot:
    def __init__(self, config: MeetJoinerConfig):
        self.config = config
        self.driver = None
        self.media_stream_driver = None
        # self.recorder = record_audio()
        self.recording_thread = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        self.driver = uc.Chrome(options=chrome_options)

    def start_websocket(self):
        """Start the WebSocket connection in a separate thread."""
        self.websocket_client = AudioWebSocketClient(
            api_key=API_KEY,  # Replace with your API key
            ws_url=WS_URL,  # Replace with your WebSocket URL
        )

        self.websocket_thread = threading.Thread(target=self.websocket_client.run)
        self.websocket_thread.start()
        print("WebSocket started.")

    def stop_websocket(self):
        """Stop the WebSocket connection."""
        if self.websocket_client:
            self.websocket_client.stop()  # Implement a stop method in your WebSocket client
            self.websocket_thread.join()  # Wait for the thread to finish
            print("WebSocket stopped.")

    def mute_audio_camera_before_join(self):
        """Mute the microphone and camera before joining the meeting."""
        try:
            # self.driver.find_element(
            #     By.XPATH, '//div[contains(@aria-label, "microphone")]'
            # ).click()
            # print("Microphone muted in preview.")

            self.driver.find_element(
                By.XPATH, '//div[contains(@aria-label, "camera")]'
            ).click()
            print("Camera muted in preview.")
        except Exception as e:
            print(f"Error muting microphone or camera: {e}")

    def select_virtual_audio_devices(self):
        """Select both 'virtual_mic' and 'virtual_speaker' from Google Meet's dropdowns."""
        try:
            mic_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[aria-label="Microphone: Default"]')
                )
            )
            mic_button.click()
            print("Microphone dropdown opened.")

            virtual_mic_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//span[text()="virtual_mic"]')
                )
            )
            virtual_mic_option.click()
            print("Virtual Microphone selected.")

            speaker_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'button[aria-label="Speaker: Default"]')
                )
            )
            speaker_button.click()
            print("Speaker dropdown opened.")

            virtual_speaker_option = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//span[text()="virtual_speaker"]')
                )
            )
            virtual_speaker_option.click()
            print("Virtual Speaker selected.")
        except Exception as e:
            print(f"Error selecting virtual devices: {e}")

    def click_mic(self):
        """Simulates Ctrl + D keypress to toggle the microphone."""
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).send_keys("d").key_up(Keys.CONTROL).perform()
        print("Microphone toggle (Ctrl + D) sent.")

    def get_participant_count(self) -> int:
        """Fetch the number of participants in the meeting."""
        try:
            sample_div = self.driver.find_element(
                By.XPATH, '//div[contains(text(), "Contributors")]'
            )
            time.sleep(5)
            contributor_count_element = sample_div.find_element(
                By.XPATH, "following-sibling::*[1]"
            )
            contributor_count = contributor_count_element.text
            print(f"Contributor Count: {contributor_count}")
            return int(contributor_count)
        except Exception as e:
            print(f"Error while fetching participant count: {e}")
            return 0

    def leave_meeting(self):
        """Leave the Google Meet session."""
        try:
            self.driver.find_element(
                By.XPATH, "//button[@aria-label='Leave call']"
            ).click()
            print("Clicked 'Leave call'. Leaving the meeting...")
        except Exception as e:
            print(f"Error while leaving the meeting: {e}")

    def is_in_meeting(self) -> bool:
        """Check if the bot has successfully joined the meeting."""
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(text(), "Guest Bot")]')
                )
            )
            print("Bot has joined the meeting.")
            return True
        except Exception as e:
            print(f"Error detecting meeting: {e}")
            return False

    def join_meeting(self):
        """Join a Google Meet session."""
        self.media_stream_driver = VirtualMediaStreamer(
            self.config.video_url, self.config.audio_url
        )
        self.media_stream_driver.unload_modules()
        self.media_stream_driver.load_virtual_audio_modules()

        self.setup_driver()
        try:
            self.driver.get(self.config.meeting_url)
            time.sleep(5)

            try:
                name_input = self.driver.find_element(
                    By.XPATH, '//input[@aria-label="Your name"]'
                )
                name_input.send_keys("Guest Bot")
                time.sleep(2)
            except Exception:
                print("No guest name required.")

            self.mute_audio_camera_before_join()
            self.select_virtual_audio_devices()

            try:
                ask_to_join_button = self.driver.find_element(
                    By.XPATH, '//span[text()="Ask to join"]'
                )
                ask_to_join_button.click()
                print("Clicked 'Ask to join'. Waiting for host approval...")
                time.sleep(20)
            except Exception:
                try:
                    join_button = self.driver.find_element(
                        By.XPATH, '//span[text()="Join now"]'
                    )
                    join_button.click()
                    print("Clicked 'Join now'.")
                except Exception:
                    print("Neither 'Ask to join' nor 'Join now' button found.")
                    return

            try:
                self.driver.find_element(
                    By.XPATH, "//button[@aria-label='People']"
                ).click()
                print("Opened participants list.")
                time.sleep(2)
            except Exception as e:
                print(f"Error opening participants list: {e}")
                return

            if self.is_in_meeting():
                print("Joined the meeting.")
                # self.start_recording()
                recorder = AudioRecorder()
                recorder.start()

                self.start_websocket()

                while True:
                    if self.get_participant_count() < 2:
                        print("Participant count dropped below 2. Leaving the meeting.")
                        self.leave_meeting()
                        break

        except Exception as e:
            print(f"Error in meeting: {e}")
        finally:
            recorder.stop()
            self.stop_websocket()
            self.media_stream_driver.unload_modules()
            self.driver.quit()
            print("Bot has left the meeting.")

    def start_recording(self):
        """Start the audio recording in a separate thread."""
        print("Recording started.")
