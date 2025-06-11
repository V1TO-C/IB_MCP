# tickler/Dockerfile
# This Dockerfile builds a lightweight image for the Tickler service.

# Use Alpine Linux as the base image for a small footprint.
FROM alpine:3.20

# Set the working directory inside the container.
WORKDIR /app

# Install curl during the image build process.
# curl is required for the healthcheck and the main tickler script to send HTTP requests.
RUN apk add --no-cache curl

# Copy the healthcheck script into the container and make it executable.
# This script will be used by Docker's healthcheck mechanism.
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Copy the main tickler script into the container and make it executable.
# This script contains the continuous polling logic for the tickler service.
COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

# Set the entrypoint for the container to run the main tickler script.
# This ensures that the 'run.sh' script is executed when the container starts.
ENTRYPOINT ["/usr/local/bin/run.sh"]
