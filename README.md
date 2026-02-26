# Multi-Modal Face Emotion & Audio Animator

Hệ thống AI xử lý ảnh tĩnh thành video khuôn mặt nói chuyện/biểu cảm với độ chân thực cao, kết hợp SOTA 2024 **LivePortrait** (cho Expression) và **SadTalker** (cho Audio-driven Lip-sync & TTS).

## 1. Yêu cầu hệ thống

- **Hệ điều hành:** Linux (Ubuntu/Debian recommended).
- **Phần cứng:** GPU NVIDIA (Tối thiểu RTX 3060 12GB VRAM. Khuyến nghị dòng RTX 4090/A100 cho tốc độ Real-time).
- **RAM:** 16GB+.

## 2. Cài đặt hệ thống (Tự động)

Hệ thống đã được đóng gói sẵn để xử lý toàn bộ quá trình clone mã nguồn, cài đặt thư viện (`PyTorch`, `ffmpeg`, `edge-tts` v.v..) và tải các Pre-trained weights cho cả 2 luồng (tổng cộng ~12GB):

```bash
chmod +x setup.sh
./setup.sh
```

**Quá trình này cần khoảng 5-10 phút** tùy thuộc vào tốc độ mạng để tải các weights từ HuggingFace và Github.

## 3. Hướng dẫn sử dụng (Inference)

File `infer.py` là Endpoint giao tiếp chính với model. Hệ thống chia làm 2 nhánh sử dụng: 
- Nhánh 1: Lái bằng Biểu cảm hình ảnh (LivePortrait).
- Nhánh 2: Lái bằng Âm thanh / Văn bản (SadTalker / Edge-TTS).

### Cú pháp chung:

```bash
python infer.py -i <đường_dẫn_ảnh> [TUỲ_CHỌN_LÁI] [-o <thư_mục_đầu_ra>]
```

### Các ví dụ:

**A. Sinh video bằng Biểu cảm hình ảnh (Dùng `-e` / `--emotion`):**
Cung cấp `smile`, `sad`, `surprise` hoặc tên file `.mp4` bất kỳ nằm trong thư mục `assets/driving_templates/`.

```bash
python infer.py -i assets/source_images/test.jpg -e smile
```

**B. Sinh video mấp máy môi khớp với Audio có sẵn (Dùng `-a` / `--audio`):**
Cung cấp file nhạc, file ghi âm giọng nói định dạng `.mp3` hoặc `.wav`.

```bash
python infer.py -i inputs/monalisa.jpg -a inputs/self_intro.mp3
```

**C. Sinh video đọc kịch bản từ Text (Dùng `-t` / `--text`):**
Hệ thống sẽ tự động tổng hợp giọng nói AI (TTS bằng Microsoft Edge) và cho khuôn mặt đọc đúng đoạn text đó. Bạn nên truyền text trong cặp ngoặc kép `""`.

```bash
python infer.py -i inputs/monalisa.jpg -t "Hello there, my name is Monalisa. Welcome to the museum!"
```
