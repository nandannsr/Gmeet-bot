import pyaudio
import wave
import threading
import time

# Parameters
CHUNK = 88200  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 2  # Stereo audio
RATE = 44100  # Sampling rate

class AudioRecorder:
    def __init__(self, filename="output.wav"):
        self.filename = filename
        self.frames = []
        self.recording = False
        self.thread = None

    def _record_audio(self):
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Recording...")

        while self.recording:
            data = stream.read(CHUNK)
            self.frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded audio to a file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print(f"Recording saved as {self.filename}")

    def start(self):
        self.recording = True
        self.thread = threading.Thread(target=self._record_audio)
        self.thread.start()

    def stop(self):
        self.recording = False
        if self.thread is not None:
            self.thread.join()  # Wait for the thread to finish

if __name__ == "__main__":
    pass
    # recorder = AudioRecorder()
    # recorder.start()

    # time.sleep(50)

    # recorder.stop()
