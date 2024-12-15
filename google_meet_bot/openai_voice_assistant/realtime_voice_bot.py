import os
import json
import base64
import numpy as np
import pyaudio
import websocket
import threading


class AudioWebSocketClient:
    def __init__(
        self, api_key, ws_url, duration=50, samplerate=24000, filename="meet_audio.wav"
    ):
        self.api_key = api_key # Open AI key
        self.ws_url = ws_url # wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01
        self.duration = duration
        self.samplerate = samplerate
        self.filename = filename
        self.wait = False

        # Audio parameters
        self.chunk = 44800  # Number of frames per buffer (2 seconds at 24kHz)
        self.format = pyaudio.paInt16  # 16-bit PCM
        self.channels = 1  # Mono
        self.rate = 24000  # Sampling rate of 24kHz
        self.silence_threshold = 1000  # Adjust threshold to detect silence
        self.silence_duration = 5  # Seconds of silence before stopping

        # State variables
        self.silent_chunks = 0  # Counter for silent frames

    def is_silent(self, data, threshold=None):
        """Check if the chunk of audio is silent."""
        threshold = threshold or self.silence_threshold
        audio_data = np.frombuffer(data, dtype=np.int16)
        print(np.abs(audio_data).mean())
        return np.abs(audio_data).mean() < threshold

    def audio_to_base64(self, audio_data):
        """Convert raw audio data to base64-encoded PCM16 data."""
        audio_data = (audio_data * 32767).astype(np.int16)  # Convert to PCM16
        return base64.b64encode(audio_data.tobytes()).decode()

    def base64_to_audio(self, base64_audio):
        """Convert base64-encoded audio back to raw audio data."""
        audio_bytes = base64.b64decode(base64_audio)
        return (
            np.frombuffer(audio_bytes, dtype=np.int16) / 32767.0
        )  # Convert back to float

    def session_update(self, ws):
        config = {
            "event_id": "event_123",
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": "Your knowledge cutoff is 2023-10. You are a helpful assistant.",
                "voice": "alloy",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": None,
            },
        }
        ws.send(json.dumps(config))

    def stop(self):
        """Close the WebSocket connection gracefully."""
        if self.ws_url:
            self.ws.close()  # Close the WebSocket connection
            print("WebSocket connection closed.")

    def on_message(self, ws, message):
        """WebSocket event handler for incoming messages."""
        event = json.loads(message)

        if event.get("type") == "response.audio.delta":
            audio_content = event["delta"]
            if audio_content:
                audio_data = self.base64_to_audio(
                    audio_content
                )  # Convert to raw audio data
                self.play_audio(audio_data)  # Play the audio immediately

        elif event.get("type") == "session.created":
            # Start recording and sending audio
            threading.Thread(target=self.record_and_send_audio, args=(ws,)).start()

        elif event.get("type") == "response.done":
            threading.Thread(target=self.record_and_send_audio, args=(ws,)).start()
            print("Received audio done event. Continuing to record.")

        elif event.get("type") == "input_audio_buffer.speech_started":
            print("speech_started:", event)

        elif event.get("type") == "input_audio_buffer.speech_stopped":
            print("speech_stopped:", event)

        elif event.get("type") == "input_audio_buffer.committed":
            print("buffer committed:", event)

    def on_open(self, ws):
        """WebSocket event handler for connection open."""
        print("Connected to server.")
        self.session_update(ws)
        print("Initial configuration sent.")

    def play_audio(self, audio_data):
        """Plays audio from raw audio data using PyAudio."""
        audio_data_pcm = (audio_data * 32767).astype(np.int16)
        # os.environ["PULSE_SINK"] = "virtual_speaker"

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Open a stream with the desired format
        stream = p.open(
            format=self.format, channels=self.channels, rate=self.rate, output=True
        )  # Output stream

        print("Playing audio...")
        stream.write(audio_data_pcm.tobytes())  # Write audio data to the stream

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()  # Terminate PyAudio
        print("Audio playback completed.")

    def send_audio_frame(self, ws, audio_data):
        """Send audio frame via WebSocket."""
        base64_audio = base64.b64encode(audio_data).decode()
        event = {"type": "input_audio_buffer.append", "audio": base64_audio}
        ws.send(json.dumps(event))
        print("Sent audio frame.")

    def commit_audio_buffer(self, ws):
        """Commit the current audio buffer when silence is detected."""
        event_commit = {"type": "input_audio_buffer.commit"}
        ws.send(json.dumps(event_commit))
        ws.send(json.dumps({"type": "response.create"}))

        print("Sent commit event.")

    def record_and_send_audio(self, ws):
        """Record audio from the microphone and send to WebSocket."""
        p = pyaudio.PyAudio()
        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        print("Recording and sending audio...")
        self.silent_chunks = 0  # Reset silent chunks counter

        while True:

            data = stream.read(self.chunk)  # Record a chunk of audio
            self.send_audio_frame(
                ws, data
            )  # Send the audio frame regardless of silence

            if self.is_silent(data):
                self.silent_chunks += 1
                print("Silent chunk detected:", self.silent_chunks)
            else:
                if self.silent_chunks > 0:
                    print("Sound detected after silence.")
                self.silent_chunks = 0  # Reset silent count if sound is detected

            # If silence persists for the specified duration, commit the audio buffer
            if self.silent_chunks * (self.chunk / self.rate) >= self.silence_duration:
                self.commit_audio_buffer(ws)
                break  # Exit loop after committing buffer

        stream.stop_stream()
        stream.close()
        p.terminate()

    def run(self):
        """Establish WebSocket connection and start recording."""
        # websocket.enableTrace(True)

        # WebSocket setup
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # Replace with your API key
            "OpenAI-Beta": "realtime=v1",
        }
        ws = websocket.WebSocketApp(
            self.ws_url, on_message=self.on_message, header=headers
        )
        self.ws = ws

        def on_open_with_audio(ws):
            self.on_open(ws)  # Send initial config
            self.record_and_send_audio(ws)  # Start recording and sending audio frames

        ws.on_open = on_open_with_audio
        ws.run_forever()