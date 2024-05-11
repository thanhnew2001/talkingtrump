import os
import time
import torch
import torchaudio
import re

from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.generic_utils import get_user_data_dir
from TTS.utils.manage import ModelManager
from transformers import MarianMTModel, MarianTokenizer
from faster_whisper import WhisperModel
from transformers import AutoTokenizer
import json
import torch
from torch.nn import functional as F
import numpy as np

import io
from pydub import AudioSegment
import base64
import uuid

from flask import (
    Flask,
    request,
    jsonify,
    make_response,
    send_file,
    render_template,
    Response,
    send_from_directory,
)
from flask_cors import CORS

from dotenv import load_dotenv

load_dotenv()

weights_relative_path = os.getenv("MODEL_DIR")
HF_TOKEN = os.getenv("HF_TOKEN_READ")

app = Flask(__name__, static_folder='static')

CORS(app)  # Enable CORS for all routes

# Directory where files are saved
FILE_DIRECTORY = os.path.join(app.root_path, "mp3")
os.makedirs(FILE_DIRECTORY, exist_ok=True)

# Initialize the Whisper model #large-v3 seems to have a problem
whisper_model = WhisperModel(f"{weights_relative_path}/faster-whisper-v3")

# Set environment variable for Coqui TTS agreement
os.environ["COQUI_TOS_AGREED"] = "1"

config_path = f"{weights_relative_path}/coqui-xtts-v2/config.json"

# Check if the config file exists after attempting to download
if os.path.exists(config_path):
    print("Model config file found. Proceeding with model initialization.")

    # Initialize the model from the configuration
    config = XttsConfig()
    config.load_json(config_path)
    xtts_model = Xtts.init_from_config(config)
    xtts_model.load_checkpoint(
        config,
        checkpoint_path=f"{weights_relative_path}/coqui-xtts-v2/model.pth",
        vocab_path=f"{weights_relative_path}/coqui-xtts-v2/vocab.json",
        eval=True,
        use_deepspeed=True,
    )
    print("CUDA Available:", torch.cuda.is_available())

    xtts_model.cuda()  # Use CUDA if available, else consider .to("cpu")

    print("Model loaded successfully.")
else:
    raise FileNotFoundError(f"Model configuration file not found at: {config_path}")

# Dictionary to store speaker encoding latents for reuse
speaker_latents_cache = {}
# Use this if there is no user_id sent
SPEAKER_WAV_PATH = "trump.wav"  # Update this path

from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
def test_xtts(text, language):
    # tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)

    if not os.path.exists("wavs"):
        os.mkdir("wavs")

    output_path = f"wavs/{uuid.uuid4()}.wav"

    # generate speech by cloning a voice using default settings
    tts.tts_to_file(text=text,
                    file_path=output_path,
                    speaker_wav=SPEAKER_WAV_PATH,
                    language=language,
                    split_sentences=True
                    )
    return output_path

def speed_up_wav(input_wav_path, output_wav_path, speed_factor=1.5):
    # Load the WAV file
    audio = AudioSegment.from_wav(input_wav_path)
    
    # Speed up the audio file
    sped_up_audio = audio.speedup(playback_speed=speed_factor)
    
    # Export the sped-up audio file
    sped_up_audio.export(output_wav_path, format="wav")

def generate_audio_mp3(prompt, language, speaker_wav_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    xtts_model.to(device)

    prompt = re.sub("([^\x00-\x7F]|\w)(\.|\。|\?)", r"\1 \2\2", prompt)
    print("prompt: ",prompt)
    # Check if speaker latents are already calculated
    if speaker_wav_path in speaker_latents_cache:
        gpt_cond_latent, speaker_embedding = speaker_latents_cache[speaker_wav_path]
    else:
        start_time_latents = time.time()
        gpt_cond_latent, speaker_embedding = xtts_model.get_conditioning_latents(
            audio_path=speaker_wav_path,
            gpt_cond_len=30,
            gpt_cond_chunk_len=4,
            max_ref_length=60,
        )
        latents_time = time.time() - start_time_latents
        # Cache the latents for future use
        speaker_latents_cache[speaker_wav_path] = (gpt_cond_latent, speaker_embedding)

    start_time_inference = time.time()

    if language == "zh":
        language = "zh-cn"
    out = xtts_model.inference(
        prompt,
        language,
        gpt_cond_latent,
        speaker_embedding,
        repetition_penalty=1.0,
        temperature=0.5,
    )
    inference_time = time.time() - start_time_inference

    output_fileid = f"{uuid.uuid4()}"
    output_filename = os.path.join(FILE_DIRECTORY, f"out_{output_fileid}.wav")
    output_filename_fast = os.path.join(FILE_DIRECTORY, f"out_{output_fileid}_fast.wav")

    print(out)
    torchaudio.save(output_filename, torch.tensor(out["wav"]).unsqueeze(0), 24000)
    try:

        #speed_up_wav(output_filename, output_filename_fast, speed_factor=1.5)
    
        # Load the WAV file
        audio = AudioSegment.from_wav(output_filename)

        # Convert the audio to MP3 and store in a BytesIO object
        mp3_io = io.BytesIO()
        audio.export(mp3_io, format="mp3", bitrate="22k")
        mp3_io.seek(0)  # Go to the beginning of the BytesIO object

        # Encode the MP3 data as a base64 string
        mp3_data = mp3_io.getvalue()
        mp3_base64 = base64.b64encode(mp3_data).decode("utf-8")

        return mp3_base64

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

xtts_supported_langs = [
    "en",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "pl",
    "tr",
    "ru",
    "nl",
    "cs",
    "ar",
    "zh-cn",
    "ja",
    "hu",
    "ko",
]

def check_language_existence(lang):
    if lang in xtts_supported_langs or lang == "zh":
        return True
    else:
        return False


from Wav2Lip import Processor

def process_wav2lip(face_path, audio_path, output_path):
    """
    Processes a video or image and audio using Wav2Lip to produce a video with the audio's lip movements.

    Args:
    face_path (str): Path to the face video or image file.
    audio_path (str): Path to the audio file (wav format).
    output_path (str): Path where the output video should be saved.
    """
    processor = Processor()
    processor.run(face_path, audio_path, output_path)

import base64

def base64_to_mp3(base64_string, output_filename):
    # Decode the base64 string
    mp3_data = base64.b64decode(base64_string)
    
    # Write the decoded bytes to an MP3 file
    with open(output_filename, 'wb') as mp3_file:
        mp3_file.write(mp3_data)



@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


# Transcribe - Translate - Speech  with additional info:
@app.route("/transcribe_speech_wav2lips", methods=["POST"])
def transcribe_speech_wav2lips():
    start_time =time.time()
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Generate random filenames for input and output files
    fileid = f"{uuid.uuid4()}"
    input_filename = os.path.join(FILE_DIRECTORY, f"in_{fileid}.mp3")
    file.save(input_filename)

    try:
        segments, info = whisper_model.transcribe(
            audio=input_filename,
            beam_size=1,
            temperature=0,
            word_timestamps=True,
            condition_on_previous_text=False,
            no_speech_threshold=0.1,
        )
        given_lang = info.language


        segment_list = []
        for segment in segments:
            segment_dict = {
                "start": "%.2f" % segment.start,
                "end": "%.2f" % segment.end,
                "text": segment.text,
            }
            segment_list.append(segment_dict)

        joined_text = " ".join([segment["text"] for segment in segment_list])
        # print(joined_text)
        # print(given_lang)
     
        # 2. Speech using XTTS
        # mp3_data = generate_audio_mp3(
        #         joined_text, "en", "trump.wav"
        #     )

        # mp3_filename = f"input_{fileid}.mp3"
        # base64_to_mp3(mp3_data, mp3_filename)

        audio_path = test_xtts(joined_text, "en")

        if not os.path.exists("mp4"):
            os.mkdir("mp4")

        process_wav2lip("trump.jpg", audio_path, f"mp4/output_{fileid}.mp4")
        end_time =time.time()
        print("Total time:",end_time-start_time)
        return send_file(f"mp4/output_{fileid}.mp4", mimetype='video/mp4')

    except Exception as e:
        # os.remove(os.path.join(FILE_DIRECTORY, input_filename))
        print(e)
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(port=5001,debug=True)
