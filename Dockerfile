FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cacheable layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ src/
COPY configs/ configs/
COPY data/ data/
COPY prompts/ prompts/
COPY pytest.ini .

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

# Default: run smoke test
CMD ["python", "-m", "src.cli.run_eval", "--config", "configs/smoke.yaml"]
