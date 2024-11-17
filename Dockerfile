# Dockerfile

FROM python:3.11-slim

# Install required packages
RUN pip install requests

# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY update-cloudflare-ip.py update-cloudflare-ip.py

# Set environment variables (configure these in Docker Compose or manually)
ENV CLOUDFLARE_API_TOKEN=""
ENV CLOUDFLARE_ACCOUNT_ID=""
ENV APPLICATION_ID=""
ENV POLICY_ID=""

# Run the script
CMD ["python", "-u", "update-cloudflare-ip.py"]
