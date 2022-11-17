# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9.15-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True
ENV PORT=80

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT
CMD streamlit run streamlit_app.py --server.port $PORT
