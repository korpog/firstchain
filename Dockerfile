# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy the pyproject.toml and poetry.lock files to the working directory
COPY pyproject.toml .

# Install dependencies using uv into the system Python environment
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]