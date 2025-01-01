# Using slim Python runtime as a base image
FROM python:3.10-slim

# Working directory in the created container
WORKDIR /app

# Copy project files from /server to working directory in container - excludes anything defined in .dockerignore
COPY server/ server/
COPY README.md .

# Install Python dependencies and your package (runs inside the container, where requirements.txt is not in a /server subfolder)
RUN pip install -r server/requirements.txt
RUN pip install -r server/requirements-dev.txt


# Start a shell (bash) in /app when the container runs
ENTRYPOINT ["/bin/bash"]