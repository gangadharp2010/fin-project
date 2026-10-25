FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

WORKDIR /app

# Copy the project into its Python package directory.
COPY . /app/fundamental_analysis_agent/

# Install Python dependencies.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
       -r /app/fundamental_analysis_agent/requirements.txt

# Run from the parent directory so package imports work.
EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "fundamental_analysis_agent/streamlit_app.py"]