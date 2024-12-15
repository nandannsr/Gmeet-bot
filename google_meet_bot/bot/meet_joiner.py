import time
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from pydantic import BaseModel
from bot.audio_recorder import record_audio
from typing import Union
from bot.models import AudioRecorderConfig, MeetJoinerConfig

from media_players.media_stream import VirtualMediaStreamer

#THIS CODE IS DEPRECEATED


def get_participant_count(driver) -> int:
    """
    Fetch the number of participants in the meeting.

    Args:
        driver: WebDriver instance.

    Returns:
        int: Number of participants.
    """
    try:
        sample_div = driver.find_element(
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


def select_virtual_audio_devices(driver):
    """Select both 'virtual_mic' and 'virtual_speaker' from Google Meet's dropdowns."""
    try:
        # Step 1: Select 'virtual_mic' from the microphone dropdown
        mic_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label="Microphone: Default"]')
            )
        )
        mic_button.click()
        print("Microphone dropdown opened.")

        # Step 2: Wait for the 'virtual_mic' option and click it
        virtual_mic_option = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//span[text()="virtual_mic"]'))
        )
        virtual_mic_option.click()
        print("Virtual Microphone selected.")

        # Step 3: Select 'virtual_speaker' from the speaker dropdown
        speaker_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[aria-label="Speaker: Default"]')
            )
        )
        speaker_button.click()
        print("Speaker dropdown opened.")

        # Step 4: Wait for the 'virtual_speaker' option and click it
        virtual_speaker_option = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//span[text()="virtual_speaker"]')
            )
        )
        virtual_speaker_option.click()
        print("Virtual Speaker selected.")

    except Exception as e:
        print(f"Error selecting virtual devices: {e}")


def mute_audio_camera_before_join(driver) -> None:
    """
    Mute the microphone and camera before joining the meeting.

    Args:
        driver: WebDriver instance.
    """
    try:
        driver.find_element(
            By.XPATH, '//div[contains(@aria-label, "microphone")]'
        ).click()
        print("Microphone muted in preview.")

        driver.find_element(By.XPATH, '//div[contains(@aria-label, "camera")]').click()
        print("Camera muted in preview.")
    except Exception as e:
        print(f"Error muting microphone or camera: {e}")


def click_mic(driver) -> None:
    """
    Simulates Ctrl + D keypress to toggle the microphone.

    Args:
        driver: WebDriver instance.
    """
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys("d").key_up(Keys.CONTROL).perform()
    print("Microphone toggle (Ctrl + D) sent.")


def click_camera(driver) -> None:
    """
    Simulates Ctrl + E keypress to toggle the camera.

    Args:
        driver: WebDriver instance.
    """
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys("e").key_up(Keys.CONTROL).perform()
    print("Camera toggle (Ctrl + E) sent.")


def is_in_meeting(driver) -> bool:
    """
    Check if the bot has successfully joined the meeting.

    Args:
        driver: WebDriver instance.

    Returns:
        bool: True if the bot is in the meeting, False otherwise.
    """
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(text(), "Guest Bot")]')
            )
        )
        print("Bot has joined the meeting.")
        return True
    except Exception as e:
        print(f"Error detecting meeting: {e}")
        return False


def leave_meeting(driver) -> None:
    """
    Leave the Google Meet session.

    Args:
        driver: WebDriver instance.
    """
    try:
        driver.find_element(By.XPATH, "//button[@aria-label='Leave call']").click()
        print("Clicked 'Leave call'. Leaving the meeting...")
    except Exception as e:
        print(f"Error while leaving the meeting: {e}")


def select_virtual_cam(driver) -> None:
    """
    Select the virtual camera for streaming.

    Args:
        driver: WebDriver instance.
    """
    try:
        time.sleep(4)
        click_camera(driver)
        icon_element = driver.find_elements(
            By.XPATH, "//button[@aria-label='Video settings']"
        )
        driver.execute_script("arguments[0].click();", icon_element[0])

        time.sleep(2)

        camera_button = driver.find_element(
            By.XPATH, "//button[@aria-label='Camera: Integrated Camera']"
        )
        driver.execute_script("arguments[0].click();", camera_button)

        virtual_cam_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[span='VirtualCam']"))
        )
        virtual_cam_option.click()

        icon_element = driver.find_elements(
            By.XPATH, "//button[@aria-label='Audio settings']"
        )
        driver.execute_script("arguments[0].click();", icon_element[0])

    except Exception as e:
        print(f"Error while selecting the virtual cam: {e}")


def join_google_meet(config: MeetJoinerConfig) -> None:
    """
    Join a Google Meet session and start recording audio.

    Args:
        config (MeetJoinerConfig): Configuration for the meeting.
    """
    media_stream_driver = VirtualMediaStreamer(config.video_url, config.audio_url)
    media_stream_driver.unload_modules()
    media_stream_driver.load_virtual_audio_modules()
    chrome_options = Options()
    chrome_options.add_argument("--use-fake-ui-for-media-stream")

    driver = uc.Chrome(options=chrome_options)

    try:
        driver.get(config.meeting_url)
        time.sleep(5)

        try:
            name_input = driver.find_element(
                By.XPATH, '//input[@aria-label="Your name"]'
            )
            name_input.send_keys("Guest Bot")
            time.sleep(2)
        except Exception:
            print("No guest name required.")

        mute_audio_camera_before_join(driver)
        select_virtual_audio_devices(driver)

        try:
            ask_to_join_button = driver.find_element(
                By.XPATH, '//span[text()="Ask to join"]'
            )
            ask_to_join_button.click()
            print("Clicked 'Ask to join'. Waiting for host approval...")
            time.sleep(20)
        except Exception:
            try:
                join_button = driver.find_element(By.XPATH, '//span[text()="Join now"]')
                join_button.click()
                print("Clicked 'Join now'.")
            except Exception:
                print("Neither 'Ask to join' nor 'Join now' button found.")
                return

        try:
            driver.find_element(By.XPATH, "//button[@aria-label='People']").click()
            print("Opened participants list.")
            time.sleep(2)
        except Exception as e:
            print(f"Error opening participants list: {e}")
            return

        if is_in_meeting(driver):
            print("Joined the meeting. Checking participant count...")

            if get_participant_count(driver) <= 1:
                print("Less than 2 participants. Waiting for 5 minutes...")
                time.sleep(300)

            if get_participant_count(driver) >= 2:
                print("Participants increased. Starting recording.")

                recorder = record_audio(
                    AudioRecorderConfig(output_file="meeting_recording.wav")
                )

                print("Playing audio...")
                click_mic(driver)
                media_stream_driver.play_audio()


                def stream_video_async():
                    media_stream_driver.run()

                stream_thread = threading.Thread(target=stream_video_async)
                stream_thread.start()

                time.sleep(5)

                select_virtual_cam(driver)

                stream_thread.join()
                click_camera(driver)
                click_mic(driver)

                while True:
                    time.sleep(10)
                    if get_participant_count(driver) <= 1:
                        print("Stopping the recording due to no participants.")
                        recorder.stop_recording()
                        leave_meeting(driver)
                        break
            else:
                print("Still less than 2 participants. Exiting the meeting.")
                leave_meeting(driver)

    except Exception as exc:
        print(str(exc))

    finally:
        recorder.stop_recording()
        # media_stream_driver.unload_modules()
        print("Quitting the driver.")
        driver.quit()
