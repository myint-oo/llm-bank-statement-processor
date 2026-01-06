FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime

WORKDIR /src

RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# apt update && apt install -y poppler-utils && apt install -y tesseract-ocr && apt install -y vi
RUN pip install --upgrade pip && pip install -r requirements.txt

# pip install --upgrade protobuf==3.20.3 sentencepiece
# export HF_HOME=/workspace/.cache


# no need
# pip install --upgrade torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117

# PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python start_api.py



COPY . .