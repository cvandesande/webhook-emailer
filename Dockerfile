FROM python:3.9-slim AS build-env

ENV PATH=$PATH:/home/nonroot/.local/bin
RUN useradd -m nonroot
USER nonroot
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt --user

FROM gcr.io/distroless/python3

COPY --from=build-env --chown=nonroot:nonroot /home/nonroot/.local/lib/python3.9 /home/nonroot/.local/lib/python3.9
COPY --from=build-env --chown=nonroot:nonroot /app /app
WORKDIR /app
USER nonroot
STOPSIGNAL SIGINT
CMD ["listener.py"]
