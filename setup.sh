#!/bin/bash
set -e

echo "Setting up Multi-Modal Face Animation System (LivePortrait + SadTalker)"

# 1. Setup system dependencies (Ubuntu/Debian)
echo "[1/4] Checking system dependencies..."
if command -v apt-get >/dev/null; then
    sudo apt-get update -y || echo "Cannot run apt-get update. Assuming dependencies are met."
    sudo apt-get install -y ffmpeg libgl1-mesa-glx cmake || echo "Skipping apt-get install for system packages."
fi

# 2. Clone Repositories
echo "[2/4] Cloning Repositories..."
if [ ! -d "LivePortrait" ]; then
    git clone https://github.com/KwaiVGI/LivePortrait.git
fi

if [ ! -d "SadTalker" ]; then
    git clone https://github.com/OpenTalker/SadTalker.git
fi

# 3. Install Python Dependencies
echo "[3/4] Installing Python Dependencies..."
# Install LivePortrait Dependencies
cd LivePortrait
pip install -r requirements.txt
pip install -U "huggingface_hub[cli]"
cd ..

# Install SadTalker Dependencies & TTS
cd SadTalker
pip install -r requirements.txt
# Hotfix for imageio/torchvision recursion and compatibility issues
pip install imageio==2.31.2 torchvision
# Fix for basicsr import issue
sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/g' /usr/local/lib/python3.11/dist-packages/basicsr/data/degradations.py || true
cd ..

# Install TTS
pip install gTTS edge-tts

# 4. Download Pre-trained Weights
echo "[4/4] Downloading Pre-trained Weights..."
# LivePortrait Weights
cd LivePortrait
huggingface-cli download KwaiVGI/LivePortrait --local-dir pretrained_weights --exclude "*.git*" "README.md" "docs"
cd ..

# SadTalker Weights
cd SadTalker
bash scripts/download_models.sh
cd ..

# 5. Setup default assets structure
echo "Setting up templates directory..."
mkdir -p assets/driving_templates
mkdir -p assets/source_images
mkdir -p outputs

# Provide default testing templates if missing
if [ ! -f "assets/driving_templates/smile.mp4" ]; then
    cp LivePortrait/assets/examples/driving/d6.mp4 assets/driving_templates/smile.mp4 || true
fi
if [ ! -f "assets/driving_templates/sad.mp4" ]; then
    cp LivePortrait/assets/examples/driving/d9.mp4 assets/driving_templates/sad.mp4 || true
fi
if [ ! -f "assets/driving_templates/surprise.mp4" ]; then
    cp LivePortrait/assets/examples/driving/d0.mp4 assets/driving_templates/surprise.mp4 || true
fi

echo " Setup Complete! You can now run the inference script.    "
echo " Example: python infer.py -i assets/source_images/test.jpg -e smile"
echo " Example: python infer.py -i path/to/image.jpg -a path/to/audio.mp3"
echo " Example: python infer.py -i path/to/image.jpg -t \"Hello there!\""
