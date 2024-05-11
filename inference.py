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

# Example usage
process_wav2lip("trump1.jpeg", "honeyimissyou.mp3", "output_path_imissyou.mp4")
