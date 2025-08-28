# SpeechService

The **SpeechService** is responsible for **audio and text processing**, offering two main functionalities:

- **TTS (Text-to-Speech)**: converts text into audio.
- **STT (Speech-to-Text)**: transcribes audio into text.

---
# 🔊 Text-to-Speech (TTS)

The **TTS** module is designed to convert text into audio.

## Technologies used
- **Python 3.12** → runtime for the service.
- **uv** → Python package manager and environment (fast and deterministic).
- **Kokoro** → responsible for converting text into audio.
- **Kafka** → used to publish messages in TTS-related topics.
- **Cloudflare R2** → stores the generated audio.

## Flow
1. Receives the text to be converted from the topic: `interview-question.text`.
2. Uses **Kokoro** to generate the audio.
3. Uploads the audio to the **R2 Bucket**.
4. Publishes the message to the topic: `interview-question.audio`.

# 🎤 Speech-to-Text (STT)

The **STT** module is designed to convert audio into text, performing audio transcription.

## Technologies used
- **Python 3.12** → runtime for the service.
- **uv** → Python package manager and environment (fast and deterministic).
- **Whisper** → responsible for transcribing audio into text.
- **Kafka** → used to publish messages in STT-related topics.
- **Cloudflare R2** → stores the audio to be transcribed.

## Flow
1. Receives the **audio file name** from the topic: `interview-answer.audio`.
2. Downloads the audio from the **R2 Bucket**.
3. Uses **Whisper** to **transcribe the audio** into text.
4. Publishes the **transcribed message** to the topic: `interview-answer.text`.

# 🖥️ Instructions to run locally

To run the project locally, you must have the following technologies installed:
- **Python 3.12**
- **uv**

> Kafka must be already running and properly configured.

## Steps to run

1. Make sure all the prerequisites above are installed and working.
2. Create a `.env` file in the project root with the following environment variables:

    - KAFKA_BOOTSTRAP=
    - R2_ENDPOINT=
    - R2_BUCKET=
    - R2_ACCESS_KEY=
    - R2_SECRET_KEY=
    - R2_AUDIO_FILE_PATH=

> Replace the above values with the real ones from your environment.

3. Run the project with the command:

```bash
uv run app.py
```
# 🐳 Instructions to run using Docker

To run the application using Docker, simply set the real values for the environment variables in the `docker-compose.yml` file, then run the following command:

```bash
docker-compose up