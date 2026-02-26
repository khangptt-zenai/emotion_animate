import os
import sys
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), "LivePortrait"))

from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_pipeline import LivePortraitPipeline

def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})

class CoreAnimator:
    def __init__(self, device_id=0):
        print("Initializing CoreAnimator and loading LivePortrait models...")
        
        self.args = ArgumentConfig()
        
        self.args.flag_use_half_precision = True
        self.args.flag_crop_driving_video = False
        self.args.device_id = device_id
        
        original_cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), "LivePortrait"))
        
        inference_cfg = partial_fields(InferenceConfig, self.args.__dict__)
        crop_cfg = partial_fields(CropConfig, self.args.__dict__)

        self.pipeline = LivePortraitPipeline(
            inference_cfg=inference_cfg,
            crop_cfg=crop_cfg
        )
        
        os.chdir(original_cwd)
        print("Models loaded successfully.")
        
        self.template_dir = os.path.join(os.path.dirname(__file__), "assets", "driving_templates")
        
    def generate_emotion(self, source_image_path, emotion, output_path="output.mp4"):
        template_path = os.path.join(self.template_dir, f"{emotion}.mp4")
        if not os.path.exists(template_path):
            template_path = os.path.join(self.template_dir, f"{emotion}.pkl")
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Driving template for emotion '{emotion}' not found at {template_path}")
            
        print(f"Applying emotion: {emotion} using template: {template_path}")
        
        self.args.source = os.path.abspath(source_image_path)
        self.args.driving = os.path.abspath(template_path)
        output_dir = os.path.abspath(os.path.dirname(output_path))
        self.args.output_dir = output_dir if output_dir else "."
        
        original_cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), "LivePortrait"))
        
        try:
            wfp, wfp_concat = self.pipeline.execute(self.args)
        finally:
            os.chdir(original_cwd)
        
        if os.path.exists(wfp):
            os.rename(wfp, output_path)
        print(f"Saved generated video to: {output_path}")
        
        return output_path

if __name__ == "__main__":
    
    print("CoreAnimator Initialization Test")
    try:
        animator = CoreAnimator()
        print("Initialization successful. GPU Available:", torch.cuda.is_available())
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to initialize: {e}")
