FROM python:3.9-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg fontconfig

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
