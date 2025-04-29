FROM python:3.10

# Set the working directory in the container
WORKDIR /backend

# Copy backend code
COPY . /backend

# Install dependencies
RUN pip install -r requirements.txt

# Expose the backend port
EXPOSE 6000

# Run the backend
CMD ["python", "backend_api.py"]