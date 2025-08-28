# Speech Service

The **SpeechService** is responsible for **audio and text processing**, offering two main functionalities:

- **TTS (Text-to-Speech)**: converts text into audio.
- **STT (Speech-to-Text)**: transcribes audio into text.

---
## Architecture Overview

The SpeechService follows a **procedural architecture**, which means that the execution flow is linear and step-by-step. Each module handles a specific task in sequence, allowing for simplicity, maintainability, and performance efficiency within the MVP scope.

**Justification for using procedural architecture:**

- **Simplicity**: Each process (TTS or STT) follows a clear sequence of operations, making the system easy to understand and maintain.
- **Performance**: Direct execution of tasks reduces overhead associated with more complex architectural patterns.
- **Maintainability**: Linear flows allow developers to easily locate and update functionality without navigating complex dependencies.
- **MVP Focus**: Procedural architecture is sufficient for the current scale and requirements of the MVP, ensuring that TTS and STT processes are robust without overengineering.

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
```
## 📦 Examples / Payloads

### Input Payload (consumed by TTS)
Topic: `interview-question.text`

The TTS service consumes a payload representing the question to be converted into audio:

**Fields:**
- `questionId` (Long): the ID of the question
- `question` (String): the text of the question

**Example JSON message:**
```json
{
  "questionId": 123,
  "question": "Explain the concept of dependency injection in Java."
}
```
### Output Payload (produced by TTS)
Topic: `interview-question.audio`

After generating the audio, the TTS service produces a payload containing the audio URL:

**Fields:**
- `questionId` (Long): the ID of the question
- `audioUrl` (String): the URL to access the generated audio

**Example JSON message:**
```json
{
  "questionId": 123,
  "audioUrl": "https://r2-bucket.example.com/audio/123_question.mp3"
}
```

### Input Payload (consumed by STT)
Topic: `interview-answer.audio`

The STT service consumes a payload representing the audio file to be transcribed:

**Fields:**
- `questionId` (Long): the ID of the question associated with the audio
- `filename` (String): the name of the audio file to be transcribed

**Example JSON message:**
```json
{
  "questionId": 123,
  "filename": "123_answer.mp3"
}
```
### Output Payload (produced by STT)
Topic: `interview-answer.text`

After transcribing the audio, the STT service produces a payload containing the text of the answer:

**Fields:**
- `questionId` (Long): the ID of the question associated with the audio
- `answerText` (String): the transcribed text from the audio

**Example JSON message:**
```json
{
  "questionId": 123,
  "answerText": "This is the transcribed answer to the question."
}
```

# 🧪 Speech Service Tests

This directory is intended for **unit and integration tests** related to the SpeechService (TTS and STT modules).

---

## Current Status

At the moment, **no tests have been implemented**.

Future tests can be added to ensure the correct functioning of the service.


# 🤝 Contribution

This section provides guidelines for contributing to the **Speech Service**.

Repository: [https://github.com/aierview/speech-service.git](https://github.com/aierview/speech-service.git)

---

## How to Contribute

1. **Clone the repository**
```bash
git clone https://github.com/aierview/speech-service.git
cd speech-service
```
2. **Create a new branch from main for your feature or fix:**
```bash
git checkout main
git pull
git checkout -b your-feature-branch
```

3. **Develop your feature or bug fix.**

4. **Commit your changes with clear messages:**
```bash
git add .
git commit -m "Describe your changes"
```
5. **git push origin your-feature-branch**
```bash
git push origin your-feature-branch
```

6. Open a Merge Request (MR) to the homolog branch. Your feature will be reviewed, and validated.
7. Once validated, open a Merge Request to the main branch following the normal workflow.

## ⚠️ Important Notes

- Always create a branch with a **descriptive name** that indicates the purpose of your changes:
   - Features: prefix with `feature/` → e.g., `feature/add-tts-queue`.
   - Bug fixes: prefix with `fix/` → e.g., `fix/audio-upload-bug`.
   - DevOps / CI-CD changes: prefix with `devops/` → e.g., `devops/docker-config`.
   - Documentation: prefix with `docs/` → e.g., `docs/update-readme`.
   - Tests: prefix with `test/` → e.g., `test/tts-unit-tests`.

- Make **small commits** to facilitate the review process.  
  Avoid large commits with multiple unrelated changes; this ensures that the review and approval process is smoother and more efficient.

> It is important that every contribution follows this branching and commit convention to maintain control and clarity over what changes are introduced into the project.

## 🚀 Roadmap / Future Features

- **Multi-language support**: Allow users to conduct interviews in multiple languages.  
  Currently, only Portuguese is supported. The next step is to add English and potentially other languages.

- **Kubernetes deployment**: Currently, the application is deployed directly on Fly.io.  
  The plan is to migrate to Kubernetes for a more professional, scalable, and manageable deployment workflow.
 
## 📝 License

This project is licensed under the **MIT License**.

---

MIT License

Copyright (c) 2025 AIRVIEW

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🔗 Useful Links
- [Whisper (OpenAI) Documentation](https://github.com/openai/whisper) – Official documentation for Whisper, used for speech-to-text transcription.
- [Kokoro Documentation](https://github.com/wosherco/kokoro) – Official documentation for Kokoro, used for text-to-speech generation.
- [Fly.io](https://fly.io/docs/) – Platform used for deploying the AIRVIEW services.
- [Apache Kafka](https://kafka.apache.org/documentation/) – Official documentation for Kafka, used for message streaming in AIRVIEW.
