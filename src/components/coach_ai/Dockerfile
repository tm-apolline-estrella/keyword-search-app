# Start from the Ubuntu image
FROM ubuntu:20.04

# Declare build arguments
ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    SSL_CERT_DIR=/etc/ssl/certs \
    LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3

# Install necessary packages and Python 3.10
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    ca-certificates \
    libasound2 \
    software-properties-common \
    wget \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3.10-venv python3.10-dev \
    && apt-get install -y python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip for Python 3.10 is installed
RUN wget https://bootstrap.pypa.io/get-pip.py \
    && python3.10 get-pip.py

# Remove existing pip3 and set symbolic link
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && rm -f /usr/bin/pip3 \
    && ln -s /usr/local/bin/pip3.10 /usr/bin/pip3

# Clean up
RUN rm -rf /var/lib/apt/lists/* \
    && rm get-pip.py

# Install OpenSSL 3.2 from sources if needed
RUN wget -O - https://www.openssl.org/source/openssl-3.2.0.tar.gz | tar zxf - \
    && cd openssl-3.2.0 \
    && ./config --prefix=/usr/local \
    && make -j $(nproc) \
    && make install_sw install_ssldirs \
    && ldconfig -v \
    && export SSL_CERT_DIR=/etc/ssl/certs

# Install poetry
RUN pip3 install "poetry==$POETRY_VERSION"

# Copy the Python project files
COPY pyproject.toml poetry.lock ./

# Install project dependencies using poetry
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-interaction

COPY . .

# Expose the port the app runs on
EXPOSE 8008

# Set the entrypoint for the container
CMD ["./docker-entrypoint.sh"]
