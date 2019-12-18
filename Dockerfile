FROM python:3-slim

WORKDIR /usr/src/DPNC

COPY requirements.txt ./
COPY DPNC.py ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["ip", "a"]
#ENTRYPOINT ["/bin/sh"]
ENTRYPOINT ["python3","/usr/src/DPNC/DPNC.py"]