from pydub import AudioSegment
import numpy as np

# Config
WAV_FILE_PATH = "LFC_09.45.wav"
OUTPUT_PATH = "LFC_09.45_noisy6.wav"
NOISE_LEVEL = 0.06  # Adjust from 0.0 (no noise) to 1.0 (very loud noise)

def add_white_noise_and_save(input_path, output_path, noise_level=NOISE_LEVEL):
    sound = AudioSegment.from_wav(input_path)
    samples = np.array(sound.get_array_of_samples())

    # Generate and add white noise
    noise = np.random.normal(0, noise_level * np.max(samples), samples.shape)
    noisy_samples = np.clip(samples + noise, -32768, 32767).astype(np.int16)

    noisy_audio = sound._spawn(noisy_samples.tobytes())

    # Save noisy audio
    noisy_audio.export(output_path, format="wav")
    print(f"✅ Noisy audio saved to {output_path}")

if __name__ == "__main__":
    add_white_noise_and_save(WAV_FILE_PATH, OUTPUT_PATH)
