"""
This script provides functionality to download and convert translation models from Hugging Face.
You can download all models or specific models based on language direction.

* Download all models:
    
    python download.py
    
Available translation directions are listed in the 'direct_model_mapping' dictionary.
"""

import os
import shutil
import subprocess
import argparse
from dotenv import load_dotenv

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from huggingface_hub import HfApi, HfFolder

# Load environment variables from .env file
load_dotenv()
# Your Hugging Face access token (replace with your actual token)
huggingface_token = os.getenv("HF_TOKEN_READ")
huggingface_home = os.getenv("HF_HOME")
weights_relative_path = os.getenv("MODEL_DIR")


def set_hf_home(hf_home=huggingface_home):
    # Load environment variables from .env file
    load_dotenv()

    # Resolve the relative path to an absolute path of project's root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    hf_home_path = os.path.join(project_root, hf_home)

    # Ensure the directory for HF_HOME exists
    if not os.path.exists(hf_home_path):
        os.makedirs(hf_home_path)
        print(f"Created directory at {hf_home_path}")

    # Define the line to add to .bashrc
    bashrc_line = f'export HF_HOME="{hf_home_path}"\n'

    # Path to .bashrc
    bashrc_path = os.path.expanduser("~/.bashrc")

    # Check if .bashrc already contains the line
    with open(bashrc_path, "r", encoding="utf-8") as bashrc:
        if bashrc_line in bashrc.readlines():
            print("HF_HOME is already set in .bashrc")
            return

    # Append the line to .bashrc
    with open(bashrc_path, "a", encoding="utf-8") as bashrc:
        bashrc.write(bashrc_line)
        print(f"Added HF_HOME to .bashrc: {bashrc_line.strip()}")


def login_to_huggingface():
    # Retrieve the Hugging Face token from environment variables
    huggingface_token = os.getenv("HF_TOKEN_READ")

    if huggingface_token:
        try:
            # Use the HfApi to set the token
            HfFolder.save_token(huggingface_token)
            print("Logged in to Hugging Face successfully.")
        except Exception as e:
            print(f"An error occurred while trying to log in: {e}")
    else:
        print("Hugging Face token not found. Please ensure HF_TOKEN_READ is set.")

def download_coqui_xtts_v2():
    """Downloads and sets up the Coqui XTTS-v2 model in the 'weights' directory, ensuring no duplicates."""

    # Ensure Git LFS is installed (https://git-lfs.github.com/)
    try:
        subprocess.check_output(["git-lfs", "--version"])
    except FileNotFoundError:
        print("Git LFS not found. Please install it to download the model.")
        return

    if not weights_relative_path:
        print(
            "Environment variable 'MODEL_DIR' is not set. Please set 'MODEL_DIR' to the desired base directory for model storage."
        )
        return

    # Check and remove any existing 'coqui-xtts-v2' model directory
    model_path = f"{weights_relative_path}/coqui-xtts-v2"
    if os.path.exists(model_path):
        print(
            f"Existing '{model_path}' directory found. Deleting to avoid duplicates..."
        )
        subprocess.run(["rm", "-rf", model_path], check=True)

    # Clone the model repository into the 'weights' directory
    print(
        f"Cloning Coqui XTTS-v2 repository into '{weights_relative_path}' directory..."
    )

    try:
        subprocess.run(
            ["git", "clone", "https://huggingface.co/coqui/XTTS-v2", model_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Cloning failed: {e}")
        return

    print(
        f"Coqui XTTS-v2 model downloaded and set up in '{weights_relative_path}' directory successfully!"
    )

def download_wav2lip():
    """Downloads and sets up the Coqui XTTS-v2 model in the 'weights' directory, ensuring no duplicates."""

    # Ensure Git LFS is installed (https://git-lfs.github.com/)
    try:
        subprocess.check_output(["git-lfs", "--version"])
    except FileNotFoundError:
        print("Git LFS not found. Please install it to download the model.")
        return

    if not weights_relative_path:
        print(
            "Environment variable 'MODEL_DIR' is not set. Please set 'MODEL_DIR' to the desired base directory for model storage."
        )
        return

    # Check and remove any existing 'coqui-xtts-v2' model directory
    model_path = f"{weights_relative_path}/wav2lip"
    if os.path.exists(model_path):
        print(
            f"Existing '{model_path}' directory found. Deleting to avoid duplicates..."
        )
        subprocess.run(["rm", "-rf", model_path], check=True)

    # Clone the model repository into the 'weights' directory
    print(
        f"Cloning Wav2Lip repository into '{weights_relative_path}' directory..."
    )
    # git clone https://huggingface.co/Eugenememe/wav2lip_ori

    try:
        subprocess.run(
            ["git", "clone", "https://huggingface.co/Eugenememe/wav2lip_ori", model_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Cloning failed: {e}")
        return

    print(
        f"Coqui Wav2Lip model downloaded and set up in '{weights_relative_path}' directory successfully!"
    )

def download_faster_whisper_v3():
    """Downloads and sets up the Faster Whisper v3 model in a directory specified by 'HF_HOME', ensuring no duplicates."""

    # Ensure Git LFS is installed (https://git-lfs.github.com/)
    try:
        subprocess.check_output(["git-lfs", "--version"])
    except FileNotFoundError:
        print("Git LFS not found. Please install it to download the model.")
        return

    if not weights_relative_path:
        print(
            "Environment variable 'MODEL_DIR' is not set. Please set 'MODEL_DIR' to the desired base directory for model storage."
        )
        return

    model_path = f"{weights_relative_path}/faster-whisper-v3"

    # Check if the "faster-whisper-large-v3" directory exists
    if os.path.exists(model_path):
        print(
            f"Existing '{model_path}' directory found. Deleting to avoid duplicates..."
        )
        subprocess.run(["rm", "-rf", model_path], check=True)

    # Clone the model repository
    print(
        f"Cloning Faster Whisper v3 repository into '{weights_relative_path}' directory..."
    )

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "https://huggingface.co/Systran/faster-whisper-large-v3",
                model_path,
            ],
            check=True,
            env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"),
        )
    except subprocess.CalledProcessError as e:
        print(f"Cloning failed: {e}")
        return

    # File size threshold (2.8GB in bytes)
    FILE_SIZE_THRESHOLD = 1024 * 1024 * 1024 * 2.8

    # Model file path
    model_file_path = f"{model_path}/model.bin"

    # Check if the model file exists and its size
    if os.path.isfile(model_file_path):
        file_size = os.path.getsize(model_file_path)
        if file_size >= FILE_SIZE_THRESHOLD:
            print(
                "model.bin already exists and is larger than 2.8GB. Skipping download."
            )
        else:
            print(
                "model.bin exists but is smaller than 2.8GB. Deleting and redownloading..."
            )
            subprocess.run(["rm", "-f", model_file_path], check=True)
            subprocess.run(
                [
                    "curl",
                    "-L",
                    "-o",
                    model_file_path,
                    "https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main/model.bin?download=true",
                ],
                check=True,
            )

    print(
        f"Faster Whisper v3 model downloaded and set up in '{weights_relative_path}' directory successfully!"
    )

def download_all_models():
    """Downloads all models specified in the direct_model_mapping."""
    # for direction, model_name in direct_model_mapping.items():
    #     model_dir = f"./{weights_relative_path}/{direction}"
    #     if os.path.exists(model_dir):
    #         print(f"Model '{model_name}' already downloaded (skipping)")
    #     else:
    #         download_and_save_model(model_name, model_dir)

    if os.path.exists(f"./{weights_relative_path}/faster-whisper-v3"):
        print("Model 'faster-whisper-v3' already downloaded (skipping)")
    else:
        download_faster_whisper_v3()

    if os.path.exists(f"./{weights_relative_path}/coqui-xtts-v2"):
        print("Model 'coqui-xtts-v2' already downloaded (skipping)")
    else:
        download_coqui_xtts_v2()
        
    if os.path.exists(f"./{weights_relative_path}/wav2lip"):
        print("Model 'wav2lip' already downloaded (skipping)")
    else:
        download_wav2lip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a translation model from Hugging Face"
    )
    parser.add_argument(
        "--cache",
        type=str,
        default=huggingface_home,
        help="Manually set the cache folder",
    )
    args = parser.parse_args()

    set_hf_home(args.cache)
    login_to_huggingface()
    download_all_models()

