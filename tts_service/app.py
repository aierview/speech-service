import boto3
import json
import numpy as np
import os
import soundfile as sf
import uuid
from botocore.client import Config
from confluent_kafka import Consumer, Producer
from dotenv import load_dotenv
from kokoro import KPipeline

# LOADING ENV
load_dotenv()

# KAFKA ENV
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")
TOPIC_IN = "interview-question.text"
TOPIC_OUT = "interview-question.audio"

# CLOUDFLARE ENV
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET", "meu-bucket")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_AUDIO_FILE_PATH = os.getenv("R2_AUDIO_FILE_PATH")

# Kafka Consumer config
consumer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    'group.id': 'tts-service-group',
    'auto.offset.reset': 'earliest'
}

# Kafka Producer config
producer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    "message.max.bytes": 10485760
}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)

s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4')
)


def generate_audio(text: str) -> str:
    lang_code = 'p'
    audio_chunks = []
    file_name = f"{uuid.uuid4()}.wav"
    output_file = f"/tmp/{file_name}"

    pipeline = KPipeline(lang_code)
    generator = pipeline(text, "pf_dora")
    for gs, ps, audio in generator:
        audio_chunks.append(audio)

    complete_audio = np.concatenate(audio_chunks)
    sf.write(output_file, complete_audio, samplerate=25000)

    audio_url = upload_audio_r2(output_file, f"{R2_AUDIO_FILE_PATH}/{file_name}")
    os.remove(output_file)
    return audio_url


def upload_audio_r2(file_path: str, object_name: str = None) -> str:
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        s3_client.upload_file(file_path, R2_BUCKET, object_name)
        url = f"{R2_ENDPOINT}/{R2_BUCKET}/{object_name}"
        print(f"✅ Upload concluído: {url}")
        return url
    except Exception as e:
        print(f"❌ Erro no upload para R2: {e}")
        raise


def delivery_report(err, msg):
    if err:
        print(f"Erro ao enviar mensagem: {err}")
    else:
        print(f"Mensagem enviada para {msg.topic()} [{msg.partition()}]")


def main():
    consumer.subscribe([TOPIC_IN])
    print(f"TTS Service ouvindo o tópico {TOPIC_IN}...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Erro no Kafka: {msg.error()}")
            continue

        try:
            data = json.loads(msg.value().decode("utf-8"))
            question = data.get("question")
            question_id = data.get("questionId")

            print(f"Recebido texto: {question}")

            audio_url = generate_audio(question)

            payload = {
                "questionId": question_id,
                "audioUrl": audio_url
            }

            producer.produce(
                TOPIC_OUT,
                json.dumps(payload).encode("utf-8"),
                callback=delivery_report
            )
            producer.flush()

        except Exception as e:
            print(f"Erro processando mensagem: {e}")
