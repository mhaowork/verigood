# Use an official Python runtime as a parent image
FROM python:3.11 as builder

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip wheel --wheel-dir=/wheels -r requirements.txt


FROM python:3.11-slim
WORKDIR /app

RUN --mount=type=bind,from=builder,source=/wheels,target=/deps/wheels \
    pip3 install -U /deps/wheels/*.whl

# Run the main program when the container launches
CMD ["python3", "-u", "./gmail_agent.py"]