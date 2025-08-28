import boto3
import json
import os
import uuid
from botocore.client import Config
from confluent_kafka import Consumer, Producer
from dotenv import load_dotenv
import whisper

# LOADING ENV
load_dotenv()

# KAFKA ENV
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")
TOPIC_IN = "interview-answer.audio"
TOPIC_OUT = "interview-answer.text"

# CLOUDFLARE R2 ENV
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET", "meu-bucket")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")

# Kafka Consumer config
consumer_conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    'group.id': 'stt-service-group',
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

model = whisper.load_model("base")


def download_audio_r2(object_name: str) -> str:
    suffix = os.path.splitext(object_name)[1] or ".wav"
    tmp_file = f"/tmp/{uuid.uuid4()}{suffix}"
    try:
        s3_client.download_file(R2_BUCKET, object_name, tmp_file)
        print(f"✅ Download concluído: {object_name}")
        return tmp_file
    except Exception as e:
        print(f"❌ Erro no download do R2: {e}")
        raise


def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]


def delivery_report(err, msg):
    if err:
        print(f"❌ Erro ao enviar mensagem: {err}")
    else:
        print(f"📤 Mensagem enviada para {msg.topic()} [{msg.partition()}]")


def main():
    consumer.subscribe([TOPIC_IN])
    print(f"🎧 STT Service ouvindo o tópico {TOPIC_IN}...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"❌ Erro no Kafka: {msg.error()}")
            continue

        try:
            data = json.loads(msg.value().decode("utf-8"))
            file_name = data.get("filename")
            question_id = data.get("questionId")

            print(f"📥 Recebido arquivo: {file_name}")

            local_file = download_audio_r2(file_name)
            text = transcribe_audio(local_file)

            # Montar payload de saída
            payload = {
                "questionId": question_id,
                "answerText": text
            }

            # Enviar para Kafka
            producer.produce(
                TOPIC_OUT,
                json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                callback=delivery_report
            )
            producer.flush()
            os.remove(local_file)
        except Exception as e:
            print(f"❌ Erro processando mensagem: {e}")
