import os
import sys
import argparse

from pydub import AudioSegment
from pydub.silence import split_on_silence


class RemoveNoiseCLI:
    def __init__(self, input_folder=None, output_folder=None, silence_thresh=-30, keep_silence=500):
        if not input_folder or not output_folder:
            parser = argparse.ArgumentParser(description="Process audio files to remove non-speech parts")
            parser.add_argument("input_folder", help="Path to the input folder containing audio files")
            parser.add_argument("output_folder", help="Path to the output folder where processed files will be saved")
            parser.add_argument("--silence_thresh", type=int, default=silence_thresh,
                                help="Silence threshold for non-speech detection")
            parser.add_argument("--keep_silence", type=int, default=keep_silence, help="Minimum silence length to keep")

            args = parser.parse_args()

            self.input_folder = args.input_folder
            self.output_folder = args.output_folder
            self.silence_thresh = args.silence_thresh
            self.keep_silence = args.keep_silence
        else:
            self.input_folder = input_folder
            self.output_folder = output_folder
            self.silence_thresh = silence_thresh
            self.keep_silence = keep_silence

    def main(self):

        if not os.path.exists(self.input_folder) or not os.path.isdir(self.input_folder):
            print("Error: Input folder does not exist or is not a directory.")
            sys.exit(1)

        if not os.path.exists(self.output_folder) or not os.path.isdir(self.output_folder):
            os.makedirs(self.output_folder)

        for file_name in os.listdir(self.input_folder):
            if file_name.lower().endswith(".wav"):
                input_file_path = os.path.join(self.input_folder, file_name)
                temp_output_path = os.path.join(self.output_folder, "temp.mp3")
                output_file_path = os.path.join(self.output_folder, file_name[:-4] + ".mp3")
                print(f"Processing {file_name}...")
                self.convert_to_mp3(input_file_path, temp_output_path)
                self.remove_non_speech_parts(temp_output_path, output_file_path, self.silence_thresh, self.keep_silence)
                os.remove(temp_output_path)
                print(f"Speech-only version saved as {output_file_path}")

        print("All audio files processed successfully.")

    def convert_to_mp3(self, input_file, output_file):
        os.system(f"ffmpeg -i \"{input_file}\" -codec:a libmp3lame -qscale:a 2 \"{output_file}\"")

    def remove_non_speech_parts(self,audio_file, output_file, silence_thresh=-30, keep_silence=500):
        # Load the audio file using pydub
        audio = AudioSegment.from_file(audio_file)

        # Process the audio in smaller chunks (10 seconds each)
        chunk_size = 10000
        audio_chunks = [audio[i:i + chunk_size] for i in range(0, len(audio), chunk_size)]

        # Split each chunk into sub-chunks based on silence (non-speech parts)
        speech_chunks = []
        for chunk in audio_chunks:
            sub_chunks = split_on_silence(chunk, min_silence_len=keep_silence, silence_thresh=silence_thresh)
            speech_chunks.extend(sub_chunks)

        # Check if speech_chunks is empty
        if not speech_chunks:
            print("No speech found in the audio.")
            return

        # Concatenate the speech chunks back into a single audio file
        result = speech_chunks[0]
        for chunk in speech_chunks[1:]:
            result += chunk

        # Export the result to the output file using MP3 format
        result.export(output_file, format="mp3")


if __name__ == "__main__":
    app = RemoveNoiseCLI()
    app.main()