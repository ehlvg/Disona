# Use a minimal Debian-based image
FROM debian:bookworm-slim

# Set environment variables to avoid writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies and build tools
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpcap-dev \
    iptables \
    zlib1g-dev \
    libcap-dev \
    libnetfilter-queue-dev \
    wget \
    curl \
    libssl-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    libgdbm-dev \
    libnss3-dev \
    make && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pyenv to manage Python versions
RUN curl https://pyenv.run | bash

# Set pyenv environment variables
ENV PATH="/root/.pyenv/bin:${PATH}"
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PATH}"

# Install Python 3.12 via pyenv
RUN pyenv install 3.12.0 && pyenv global 3.12.0

# Ensure pip is up-to-date
RUN python -m pip install --upgrade pip

# Install poetry for dependency management
RUN pip install poetry

# Clone the zapret repository during the build process
RUN git clone https://github.com/bol-van/zapret.git /opt/zapret

# Set the working directory
WORKDIR /bot-dnd

# Add the pyproject.toml file and install dependencies using poetry
ADD pyproject.toml .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .
