FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y git && yum clean all

COPY ffmpeg /usr/local/bin/ffmpeg
RUN chmod +x /usr/local/bin/ffmpeg

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

RUN mkdir -p /opt/ml/models
RUN python3 -c "import whisper; model = whisper.load_model('base', download_root='/opt/ml/models')"

COPY app.py .

ENV PYTHONUNBUFFERED=1
ENV WHISPER_CACHE_DIR=/opt/ml/models

CMD [ "app.lambda_handler" ]

