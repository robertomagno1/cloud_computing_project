# Use AWS Lambda Python base image (x86_64)
FROM public.ecr.aws/lambda/python:3.9

# Set environment variables
ENV PYTHONPATH=/var/task

# Install system dependencies
RUN yum update -y && \
    yum install -y wget tar xz && \
    yum clean all

# Install ffmpeg (static build for Lambda)
RUN wget -q https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz -O /tmp/ffmpeg.tar.xz && \
    cd /tmp && \
    tar xf ffmpeg.tar.xz && \
    cp ffmpeg-git-*-amd64-static/ffmpeg /usr/local/bin/ && \
    cp ffmpeg-git-*-amd64-static/ffprobe /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe && \
    rm -rf /tmp/ffmpeg*

# Copy requirements first for better caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py ${LAMBDA_TASK_ROOT}/

# Set Lambda handler
CMD ["app.lambda_handler"]
