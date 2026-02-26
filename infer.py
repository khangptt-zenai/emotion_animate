import os
import argparse
import sys
import subprocess
import shutil

try:
    from animator import CoreAnimator
except ImportError:
    print("Error: Could not import CoreAnimator. Make sure animator.py is in the current directory.")
    sys.exit(1)

def text_to_speech(text, output_audio_path):
    print(f"Generating TTS audio for text: '{text}'...")
    # Use edge-tts to generate audio
    cmd = [
        "edge-tts",
        "--text", text,
        "--voice", "en-US-AriaNeural",
        "--write-media", output_audio_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"TTS Audio saved to {output_audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating TTS: {e.stderr.decode()}")
        sys.exit(1)

def run_sadtalker(image_path, audio_path, output_dir, output_filename):
    print(f"Running SadTalker (Audio-Driven Animation)...")
    sadtalker_dir = os.path.join(os.path.dirname(__file__), "SadTalker")
    
    if not os.path.exists(sadtalker_dir):
        print("Error: SadTalker directory not found. Please ensure setup.sh installed it properly.")
        sys.exit(1)
        
    # SadTalker outputs to a timestamped subfolder by default. 
    # We will use a temp result dir, then move the result to the desired path.
    temp_result_dir = os.path.join(output_dir, "sadtalker_temp")
    os.makedirs(temp_result_dir, exist_ok=True)
    
    cmd = [
        "python", "inference.py",
        "--driven_audio", os.path.abspath(audio_path),
        "--source_image", os.path.abspath(image_path),
        "--result_dir", os.path.abspath(temp_result_dir),
        "--still",
        "--preprocess", "crop",
        "--enhancer", "gfpgan"
    ]
    
    try:
        # Run from SadTalker dir
        subprocess.run(cmd, cwd=sadtalker_dir, check=True)
        
        # Find the generated video in the temp directory
        # SadTalker creates a timestamped folder inside result_dir
        generated_file = None
        for root, _, files in os.walk(temp_result_dir):
            for file in files:
                if file.endswith(".mp4") and "enhanced" in file: # prioritize enhanced video
                    generated_file = os.path.join(root, file)
                    break
        
        if not generated_file:
            # Fallback if no 'enhanced' string is found
            for root, _, files in os.walk(temp_result_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        generated_file = os.path.join(root, file)
                        break
                        
        if generated_file:
            final_output_path = os.path.join(output_dir, output_filename)
            shutil.move(generated_file, final_output_path)
            shutil.rmtree(temp_result_dir) # cleanup temp dir
            return final_output_path
        else:
            print("Error: SadTalker finished but no output video was found.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error during SadTalker generation: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Emotion & Audio Face Animator")
    parser.add_argument("-i", "--image", required=True, help="Path to the input portrait image.")
    
    # Optional inputs (user must provide at least one to drive the face)
    parser.add_argument("-e", "--emotion", help="Type of emotion: 'smile', 'sad', 'surprise', or your custom template.")
    parser.add_argument("-a", "--audio", help="Path to a driving audio file (.mp3, .wav) to sync lips.")
    parser.add_argument("-t", "--text", help="Text string to synthesize voice and animate the face.")
    
    parser.add_argument("-o", "--output_dir", default="outputs", help="Directory to save the generated output. Default: 'outputs/'")
    
    args = parser.parse_args()

    # 1. Validate Input Combinations
    if not (args.emotion or args.audio or args.text):
        print("Error: You must specify at least one driving method: --emotion, --audio, or --text.")
        sys.exit(1)
        
    if not os.path.exists(args.image):
        print(f"Error: Input image '{args.image}' not found.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 2. Process Based on Engine Type
    base_name = os.path.basename(args.image).split('.')[0]
    
    if args.audio or args.text:
        # ---------------------------------------------------------
        # MODE: AUDIO-DRIVEN (SadTalker)
        # ---------------------------------------------------------
        driving_audio_path = args.audio
        
        if args.text:
            output_filename = f"animated_{base_name}_text.mp4"
            # Gen TTS first
            driving_audio_path = os.path.join(args.output_dir, f"temp_{base_name}_tts.wav")
            text_to_speech(args.text, driving_audio_path)
        else:
            # Generate from provided audio
            output_filename = f"animated_{base_name}_audio.mp4"
            
        print("====================================")
        print(" Starting SadTalker (Audio Mode)    ")
        print(f"Input Image : {args.image}")
        print(f"Input Audio : {driving_audio_path}")
        print("====================================")
        
        final_video_path = run_sadtalker(args.image, driving_audio_path, args.output_dir, output_filename)
        
        print(f"[SUCCESS] Video saved successfully to {final_video_path}")
        
        # Cleanup temporary TTS audio if created
        if args.text and os.path.exists(driving_audio_path):
            os.remove(driving_audio_path)
            
    elif args.emotion:
        # ---------------------------------------------------------
        # MODE: EMOTION-DRIVEN (LivePortrait)
        # ---------------------------------------------------------
        output_filename = f"animated_{base_name}_{args.emotion}.mp4"
        output_path = os.path.join(args.output_dir, output_filename)

        print("====================================")
        print(" Starting LivePortrait Core Animator")
        print(f"Input Image : {args.image}")
        print(f"Emotion     : {args.emotion}")
        print(f"Output Path : {output_path}")
        
        try:
            animator = CoreAnimator()
            animator.generate_emotion(
                source_image_path=args.image,
                emotion=args.emotion,
                output_path=output_path
            )
            print(f"[SUCCESS] Video saved successfully to {output_path}")
            
        except FileNotFoundError as fnf_error:
            print(f"[ERROR] {fnf_error}")
            print("Please check your assets/driving_templates folder for the correct templates.")
            sys.exit(1)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[ERROR] An unexpected error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
