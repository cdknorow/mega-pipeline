"""
Module that contains the command line app.
"""
import argparse
import ffmpeg
import os
from tempfile import TemporaryDirectory
import io

# Imports the Google Cloud client library
from google.cloud import speech


def download(gcp_project, bucket_name, filename):
    print("download")

    from google.cloud import storage

    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    # Find all content in a bucket
    blobs = bucket.list_blobs(prefix="input_audios/")
    for blob in blobs:
        if not blob.name.endswith("/") and os.path.basename(blob.name) == filename:
            print(blob.name)
            blob.download_to_filename(blob.name)


def transcribe(audio_path: str):
    """Transcribe audio using google speach to text API

    Args:
        audio_path (str): Path to audio to transcribe

    Returns:
        _type_: transcription
    """
    print("transcribe")

    # Instantiates a client
    client = speech.SpeechClient()

    with TemporaryDirectory() as audio_dir:
        flac_path = os.path.join(audio_dir, "audio.flac")
        stream = ffmpeg.input(audio_path)
        stream = ffmpeg.output(stream, flac_path)
        ffmpeg.run(stream)

        with io.open(flac_path, "rb") as audio_file:
            content = audio_file.read()

        # Transcribe
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(language_code="en-US")
        operation = client.long_running_recognize(config=config, audio=audio)
        response = operation.result(timeout=90)
        print(response)

        for result in response.results:
            print("Transcript: {}".format(result.alternatives[0].transcript))

        with open(
            os.path.join("text_prompts", os.path.basename(audio_path)[:-4] + ".txt"),
            "w",
        ) as out:
            out.write(response.results[0].alternatives[0].transcript)

        return response.results[0].alternatives[0].transcript


def upload(gcp_project: str, bucket_name: str, filename: str):
    """_summary_

    Args:
        gcp_project (str): GCP Project Name
        bucket_name (str): GCP Reference Bucket
        file_path (str): Path to local file
        destination_blob_name (str): Destination path in GCS
    """
    print("upload")
    from google.cloud import storage

    # Initiate Storage client
    storage_client = storage.Client(project=gcp_project)

    # Get reference to bucket
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(os.path.join("text_prompts", filename))

    blob.upload_from_filename(os.path.join("text_prompts", filename))


def main(args=None):

    gcp_project = "ai5-project"
    bucket_name = "ai5-mega-pipeline-bucket"
    input_audios = "input_audios"
    text_prompts = "text_prompts"
    filename = "input-07.mp3"
    text_prompt_name = "input-07.txt"
    audio_path = os.path.join("input_audios", filename)

    print("Args:", args)

    if args.download:
        download(gcp_project=gcp_project, bucket_name=bucket_name, filename=filename)
    if args.transcribe:
        transcribe(audio_path)
    if args.upload:
        upload(
            gcp_project=gcp_project, bucket_name=bucket_name, filename=text_prompt_name
        )


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Transcribe audio file to text")

    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="Download audio files from GCS bucket",
    )

    parser.add_argument(
        "-t", "--transcribe", action="store_true", help="Transcribe audio files to text"
    )

    parser.add_argument(
        "-u",
        "--upload",
        action="store_true",
        help="Upload transcribed text to GCS bucket",
    )

    args = parser.parse_args()

    main(args)
