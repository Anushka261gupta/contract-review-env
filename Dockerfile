# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy project files
COPY . /app

# Install uv for fast, reproducible installs
RUN pip install --no-cache-dir uv

# Install dependencies using uv (respects uv.lock)
RUN uv pip install --system --no-cache \
    fastapi>=0.110.0 \
    "uvicorn[standard]>=0.29.0" \
    pydantic>=2.0.0 \
    openenv-core>=0.2.0 \
    openai>=1.0.0 \
    python-dotenv>=1.0.0

# Install the local package itself
RUN pip install --no-cache-dir -e .

# Expose HF Spaces port
EXPOSE 7860

# Use the registered entry point (defined in pyproject.toml [project.scripts])
CMD ["server"]
