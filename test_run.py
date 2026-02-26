import os
from animator import CoreAnimator

def main():
    animator = CoreAnimator()
    
    source_img = "assets/source_images/test.jpg"
    
    emotions = ["smile", "sad", "surprise"]
    
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    for emotion in emotions:
        print(f"\n--- Generating {emotion} ---")
        out_path = os.path.join(output_dir, f"test_output_{emotion}.mp4")
        try:
            animator.generate_emotion(source_img, emotion, out_path)
            print(f"Success: {out_path}")
        except Exception as e:
            print(f"Failed to generate {emotion}: {e}")

if __name__ == "__main__":
    main()
