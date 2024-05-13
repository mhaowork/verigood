# Use an official Python runtime as a parent image
FROM python:3.11 as builder

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip3 wheel --wheel-dir=/wheels -r requirements.txt


FROM python:3.11-slim

RUN --mount=type=bind,from=builder,source=/wheels,target=/deps/wheels \
    pip3 install -U /deps/wheels/*.whl

# Copy the necessary contents into the container at /app
COPY gmail_agent.py /app
# (YOU NEED TO DOWNLOAD YOUR OWN CREDENTIALS FILE FROM GOOGLE):
COPY credentials.json /app


# Run the main program when the container launches
CMD ["python3", "./gmail_agent.py"]