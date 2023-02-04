# Must use a Cuda version 11+
FROM pytorch/pytorch:1.11.0-cuda11.3-cudnn8-runtime

WORKDIR /

# Install git
RUN apt-get update && apt-get install -y git ffmpeg liblzma-dev curl p7zip-full fuse
RUN curl https://rclone.org/install.sh | bash
ADD rclone.conf .
RUN mkdir -p /root/.config/rclone/
RUN rclone config file
RUN cp -r rclone.conf /root/.config/rclone/rclone.conf
RUN mkdir -p /root/gdrive

# Install python packages
RUN pip3 install --upgrade pip
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# We add the banana boilerplate here
ADD server.py .
EXPOSE 8000

# Add your huggingface auth key here
ENV HF_AUTH_TOKEN=hf_

# Add your model weight files 
# (in this case we have a python script)
ADD download.py .
RUN python3 download.py

# Add your custom app code, init() and inference()
ADD app.py .

CMD python3 -u server.py
CMD /usr/bin/rclone mount gdrive:/ /root/gdrive