# Stage 1: Builder
# Use full Python image to compile dependencies (useful if some packages need gcc)
FROM python:3.10-slim as builder

WORKDIR /app

# Install build tools if necessary (not strictly needed for pure wheels but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a temporary location
# --user installs to /root/.local, which makes copying easier
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
# Copy only the installed packages to a clean, slim image
FROM python:3.10-slim as final

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Ensure scripts in .local are in PATH
ENV PATH=/root/.local/bin:$PATH

# Copy app code
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "PAE_frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
