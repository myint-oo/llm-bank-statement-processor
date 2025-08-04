FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime

WORKDIR /src

RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# pip install --upgrade protobuf==3.20.3 sentencepiece
# apt update && apt install -y poppler-utils
# apt update && apt install -y tesseract-ocr


# no need
# pip install --upgrade torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117


COPY . .