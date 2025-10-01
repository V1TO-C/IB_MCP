FROM eclipse-temurin:21

WORKDIR /app

# Install unzip
RUN apt-get update && apt-get install -y unzip

# Download and unzip client portal gateway
RUN mkdir api_gateway && cd api_gateway && \
    curl -O https://download2.interactivebrokers.com/portal/clientportal.gw.zip && \
    unzip clientportal.gw.zip && rm clientportal.gw.zip

# Create the directory where the config file is expected
RUN mkdir -p api_gateway/root

# Copy our config so that the gateway will use it
COPY conf.yaml api_gateway/root/conf.yaml

# Make the entrypoint script executable
COPY run_gateway.sh /app/run_gateway.sh
RUN chmod +x /app/run_gateway.sh

# Copy the healthcheck script and make it executable
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Copy the tickler script and make it executable
COPY tickler.sh /app/tickler.sh
RUN chmod +x /app/tickler.sh

# Install curl for the tickler script
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# By default, the gateway will listen on port 5000
EXPOSE 5055

ENTRYPOINT ["/app/run_gateway.sh", "api_gateway/root/conf.yaml"]

CMD api_gateway/bin/run.sh api_gateway/root/conf.yaml
