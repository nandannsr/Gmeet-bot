<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<h1>Google Meet Bot - Auto Join, Record, and Voice Interaction</h1>

<p>This Python project creates an automated bot that joins a Google Meet meeting, records audio, interacts with participants using OpenAI's real-time voice assistant, and auto-exits when the host leaves or when the bot is the only participant remaining in the meeting. The bot uses <code>undetected-chromedriver</code> for web automation, <code>pyaudio</code> to record the audio stream, and OpenAI's real-time voice assistant API for interactive conversations.</p>

<h2>Features</h2>
<ul>
    <li><strong>Automatic Google Meet Joining</strong>: The bot can join a Google Meet session as a guest.</li>
    <li><strong>Mute Microphone and Camera</strong>: Ensures the bot does not transmit audio or video during the session.</li>
    <li><strong>Audio Recording</strong>: Records audio from the meeting using <code>pyaudio</code>.</li>
    <li><strong>Voice Interaction</strong>: Participants can talk to the bot, and it responds using OpenAI's real-time voice assistant API.</li>
</ul>

<h2>Folder Structure</h2>
<pre>
.
├── google_meet_bot
│   ├── bot
│   │   ├── __init__.py            # Init file for bot module
│   │   ├── _pycache_             # Cached Python files
│   │   ├── meet_joiner_v2.py     # Updated logic for joining Google Meet
│   │   ├── meet_joiner.py        # Original logic for joining Google Meet
│   │   ├── models.py             # Pydantic models for configuration
│   │   └── utils.py              # Helper utility functions for bot operations
│   ├── openai_voice_assistant
│   │   ├── __pycache__           # Cached Python files
│   │   ├── realtime_voice_bot.py # Logic for real-time voice interactions with OpenAI
│   │── config.py                 # Configuration for the bot
│   ├── main.py                   # Entry point for starting the bot
│   └── requirements.txt          # Python dependencies
├── .env                          # Environment variables (e.g., API keys)
└── README.md                     # Project readme
</pre>

<h2>Requirements</h2>
<p>Make sure you have the following installed:</p>
<ul>
    <li>Python 3.8+</li>
    <li>Google Chrome (or Chromium)</li>
</ul>

<h3>Python Libraries</h3>
<pre>
pip install -r requirements.txt
</pre>
<p>This will install all the necessary Python dependencies, including:</p>
<ul>
    <li><code>undetected-chromedriver</code></li>
    <li><code>selenium</code></li>
    <li><code>pyaudio</code></li>
    <li><code>openai</code></li> <!-- New addition for OpenAI integration -->
</ul>

<h3>System Dependencies</h3>
<p>To get <code>pyaudio</code> working, you may need to install some system-level dependencies, especially for Linux and macOS users:</p>

<h4>For Debian/Ubuntu-based Systems:</h4>
<pre>
sudo apt update
sudo apt install -y python3-dev portaudio19-dev python3-pyaudio
</pre>

<h2>Usage</h2>

<h3>Step 1: Set Up the Configuration</h3>
<p>Update the <code>google_meet_bot/openai_voice_assistant/config.py</code> file with your Google Meet URL as well as other configuration settings for your meeting.</p>

<h3>Step 2: Start the Bot</h3>
<pre>
python3 google_meet_bot/main.py
</pre>
<p>This will start the bot, which will:</p>
<ul>
    <li>Automatically join the Google Meet session,</li>
    <li>Mute audio and video,</li>
    <li>Record the session audio,</li>
    <li>Allow participants to interact with the bot using voice,</li>
    <li>Respond using OpenAI's real-time voice assistant API,</li>
    <li>Exit the meeting when the host leaves or the bot is the only participant remaining.</li>
</ul>
<p>The audio is saved as a WAV file after the session ends.</p>

<h2>License</h2>
<p>This project is licensed under the MIT License. Feel free to modify and distribute as per the terms of the license.</p>

</body>
</html>
