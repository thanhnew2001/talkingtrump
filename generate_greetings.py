#!/usr/bin/env python3
"""
Script to generate Trump greeting audio files using Replicate API
Run this script to create pre-generated greeting audio files
"""

import requests
import json
import os
import time

# Your Replicate API token - set this as an environment variable
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Trump voice reference URL
TRUMP_VOICE_URL = "https://736930aa.talkingtrump.pages.dev/trump_voice.wav"

# Greetings to generate
GREETINGS = [
    "Hello there! Great to see you!",
    "Welcome! Let me tell you something fantastic!",
    "Hey! How are you doing today?",
    "Good to have you here!",
    "Welcome aboard! This is going to be tremendous!",
    "Hello! Ready to make some great conversation?",
    "Hey there! Let's talk about some incredible things!",
    "Welcome! I'm excited to chat with you!"
]

def generate_voice(text, output_filename):
    """Generate voice using Replicate API"""
    if not REPLICATE_API_TOKEN:
        print("❌ Error: REPLICATE_API_TOKEN environment variable not set")
        return False
    
    url = "https://api.replicate.com/v1/predictions"
    
    data = {
        "version": "e965838de46580210694f81ede74e91f010d34a310e12a8e25e242797181f7ea",
        "input": {
            "text": text,
            "voice_a": "custom_voice",
            "voice_b": "disabled",
            "voice_c": "disabled", 
            "voice_d": "disabled",
            "preset": "fast",
            "seed": 0,
            "num_autoregressive_samples": 1,
            "diffusion_iterations": 30,
            "temperature": 0.8,
            "length_penalty": 1.0,
            "repetition_penalty": 2.0,
            "top_p": 0.8,
            "max_mel_tokens": 500,
            "cvvp_amount": 0.0,
            "breathing_room": 0.0,
            "custom_voice": TRUMP_VOICE_URL
        }
    }
    
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"🎤 Generating voice for: '{text}'")
        
        # Create prediction
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        prediction = response.json()
        prediction_id = prediction["id"]
        
        print(f"⏳ Prediction created: {prediction_id}")
        
        # Poll for completion
        while True:
            response = requests.get(f"{url}/{prediction_id}", headers=headers)
            response.raise_for_status()
            
            prediction = response.json()
            status = prediction["status"]
            
            if status == "succeeded":
                audio_url = prediction["output"]
                if isinstance(audio_url, list):
                    audio_url = audio_url[0]
                
                print(f"✅ Voice generated successfully!")
                
                # Download the audio file
                audio_response = requests.get(audio_url)
                audio_response.raise_for_status()
                
                # Save to file
                os.makedirs("public/greetings", exist_ok=True)
                with open(f"public/greetings/{output_filename}", "wb") as f:
                    f.write(audio_response.content)
                
                print(f"💾 Saved as: public/greetings/{output_filename}")
                return True
                
            elif status == "failed":
                print(f"❌ Voice generation failed: {prediction.get('error', 'Unknown error')}")
                return False
                
            else:
                print(f"⏳ Status: {status}, waiting...")
                time.sleep(2)
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Generate all greeting audio files"""
    print("🎯 Starting Trump greeting generation...")
    print(f"📁 Output directory: public/greetings/")
    
    if not REPLICATE_API_TOKEN:
        print("❌ Error: Please set REPLICATE_API_TOKEN environment variable")
        print("   Example: export REPLICATE_API_TOKEN='your_token_here'")
        return
    
    success_count = 0
    
    for i, greeting in enumerate(GREETINGS, 1):
        output_filename = f"greeting{i}.wav"
        print(f"\n📝 Processing greeting {i}/{len(GREETINGS)}")
        
        if generate_voice(greeting, output_filename):
            success_count += 1
        else:
            print(f"❌ Failed to generate greeting {i}")
        
        # Add delay between requests to be respectful
        if i < len(GREETINGS):
            time.sleep(3)
    
    print(f"\n🎉 Generation complete!")
    print(f"✅ Successfully generated: {success_count}/{len(GREETINGS)} greetings")
    
    if success_count > 0:
        print(f"📁 Files saved in: public/greetings/")
        print("🎵 You can now use these greeting files in your app!")

if __name__ == "__main__":
    main()
