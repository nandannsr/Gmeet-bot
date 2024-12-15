import subprocess
import re
import os
import pyaudio, wave


class VirtualMediaStreamer:
    def __init__(
        self,
        video_path="/home/nandan/Downloads/hello.mp4",
        audio_path="/home/nandan/Music/Gmeet_Bot/google_meet_bot/media_players/text.wav",
    ):
        self.video_path = video_path
        self.virtual_cam_device = None
        self.audio_path = audio_path

    def load_virtual_audio_modules(self):
        """Loads PulseAudio modules for virtual audio devices."""
        try:
            print("Loading virtual speaker...")
            subprocess.run(
                [
                    "pactl",
                    "load-module",
                    "module-null-sink",
                    "sink_name=virtual_speaker",
                    'sink_properties=device.description="virtual_speaker"',
                ],
                check=True,
            )

            print("Loading virtual microphone...")
            subprocess.run(
                [
                    "pactl",
                    "load-module",
                    "module-remap-source",
                    "master=virtual_speaker.monitor",
                    "source_name=virtual_mic",
                    'source_properties=device.description="virtual_mic"',
                ],
                check=True,
            )

            # Set the PULSE_SINK environment variable to virtual_speaker
            os.environ["PULSE_SINK"] = "virtual_speaker"
            print("Virtual audio modules loaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error loading virtual audio modules: {e}")
            exit(1)

    def unload_virtual_audio_modules(self):
        """Unloads PulseAudio modules for virtual audio devices."""
        try:
            print("Unloading virtual audio modules...")
            subprocess.run(
                ["pactl", "unload-module", "module-remap-source"], check=True
            )
            subprocess.run(["pactl", "unload-module", "module-null-sink"], check=True)
            print("Virtual audio modules unloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error unloading virtual audio modules: {e}")
            exit(1)

    def create_virtual_cam(self):
        """Creates a virtual webcam using v4l2loopback."""
        try:
            print("Creating virtual webcam...")
            subprocess.run(
                [
                    "sudo",
                    "modprobe",
                    "v4l2loopback",
                    "video_nr=3",
                    'card_label="VirtualCam"',
                    "exclusive_caps=1",
                ],
                check=True,
            )
            self.virtual_cam_device = (
                self.list_video_devices()
            )  # Get the virtual camera device path
            print("Virtual webcam created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual webcam: {e}")
            exit(1)

    def stop_virtual_cam(self):
        """Stops the virtual webcam by removing the v4l2loopback module."""
        try:
            print("Stopping virtual webcam...")
            subprocess.run(
                ["sudo", "modprobe", "--force", "-r", "v4l2loopback"], check=True
            )
            print("Virtual webcam stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error stopping virtual webcam: {e}")
            exit(1)

    def list_video_devices(self):
        """Lists video devices and returns the path of the virtual camera."""
        try:
            output = subprocess.check_output(["v4l2-ctl", "--list-devices"]).decode()
            # Extract the virtual camera path using regex
            match = re.search(r"VirtualCam\s*.*\n\s*(\/dev\/video\d+)", output)
            if match:
                return match.group(1)
            else:
                print("Virtual camera not found.")
                exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error listing video devices: {e}")
            exit(1)

    def stream_video_and_audio(self):
        """Streams video and audio to virtual camera and microphone using ffmpeg."""
        if not self.virtual_cam_device:
            print(
                "Virtual camera device is not set. Please create the virtual camera first."
            )
            return

        ffmpeg_command = [
            "ffmpeg",
            "-re",
            "-i",
            self.video_path,  # Path to the video file
            "-f",
            "v4l2",
            self.virtual_cam_device,  # Use detected virtual camera
            "-f",
            "pulse",
            "demo_stream",  # Virtual microphone
        ]

        subprocess.run(ffmpeg_command)

    def play_audio(self):
        """Plays audio to the virtual microphone using PyAudio."""
        # Open the audio file
        wf = wave.open(self.audio_path, 'rb')

        # Instantiate PyAudio
        p = pyaudio.PyAudio()

        # Open a stream with PyAudio settings matching the WAV file
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Read data from the WAV file and play it through the stream
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        print("Audio playback completed.")


    def unload_modules(self):
        self.unload_virtual_audio_modules()
        self.stop_virtual_cam()

    def run(self):
        """Main method to manage the virtual media streaming lifecycle."""
        self.create_virtual_cam()
        self.stream_video_and_audio()


# Example Usage
if __name__ == "__main__":
    streamer = VirtualMediaStreamer(
        "/home/nandan/Downloads/hello.mp4", "/home/nandan/Downloads/output.wav"
    )
    streamer.load_virtual_audio_modules()
    import time
    # time.sleep(5)
    # streamer.play_audio()
    streamer.unload_modules()


