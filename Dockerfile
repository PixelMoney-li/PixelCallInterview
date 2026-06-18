FROM python:3.12-slim

WORKDIR /app
COPY . .

# Standard library only — no dependencies to install.
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "-m", "pixel_call.service"]
