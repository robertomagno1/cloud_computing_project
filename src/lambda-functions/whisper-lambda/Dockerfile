FROM public.ecr.aws/lambda/python:3.9

# Installa git e altre dipendenze di sistema
RUN yum install -y git && yum clean all

# Aggiunge ffmpeg
COPY ffmpeg /usr/local/bin/ffmpeg
RUN chmod +x /usr/local/bin/ffmpeg

# Aggiorna pip e installa dipendenze Python
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Crea directory per i modelli Whisper
RUN mkdir -p /opt/ml/models

# Scarica il modello Whisper Base durante la build
# Questo evita il download a runtime e migliora le performance
RUN python3 -c "import whisper; model = whisper.load_model('base', download_root='/opt/ml/models')"

# Copia il codice della Lambda
COPY app.py .

# Imposta le variabili d'ambiente per ottimizzazione
ENV PYTHONUNBUFFERED=1
ENV WHISPER_CACHE_DIR=/opt/ml/models

# Entry point per AWS Lambda
CMD [ "app.lambda_handler" ]