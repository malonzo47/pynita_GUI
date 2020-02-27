#### Use latest Ubuntu
FROM ubuntu:latest

# Add user
RUN adduser --quiet --disabled-password user

# Update base container install
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y software-properties-common
RUN add-apt-repository universe

# Install python3 and dev dependencies
RUN apt-get install -y \
    python3-pip \
    python3-pyqt5\
    libgdal-dev \
    locales \
    libgl1-mesa-glx \
    autoconf \
    build-essential \
    bzip2 \
    curl \
    gcc \
    git \
    groff \
    lib32stdc++6 \
    lib32z1 \
    lib32z1-dev \
    lib32ncursesw5 \
    libc6-dev \
    libgmp-dev \
    libmpc-dev \
    libmpfr-dev \
    libxslt-dev \
    libxml2-dev \
    m4 \
    make \
    ncurses-dev \
    ocaml \
    openssh-client \
    pkg-config \
    rsync \
    unzip \
    wget \
    zip \
    zlib1g-dev \
    cmake \
    pyqt5-dev-tools \
    python3-pip \
    python3-dev \
    libffi-dev \
    libssl-dev \
    xvfb \
    qttools5-dev-tools \
    --no-install-recommends

# Ensure locales configured correctly
RUN locale-gen en_US.UTF-8
ENV LC_ALL='en_US.utf8'

# Set python aliases for python3
RUN echo 'alias python=python3' >> ~/.bashrc
RUN echo 'alias pip=pip3' >> ~/.bashrc

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# install system and pip-compiler
RUN pip3 install --upgrade pip &&\
    pip3 install --upgrade setuptools && \
    pip3 install pip-tools

# install pygdal
RUN pip3 install \
    pygdal=="`gdal-config --version`.*" \
    backcall==0.1.0 \
    configobj==5.0.6 \
    cycler==0.10.0 \
    cython==0.29.15 \
    decorator==4.4.1 \
    ipython-genutils==0.2.0  \
    ipython==7.12.0 \
    jedi==0.16.0  \
    kiwisolver==1.1.0 \
    lxml==4.5.0 \
    matplotlib==3.1.3 \
    numpy==1.18.1 \
    pandas==1.0.1 \
    parso==0.6.2 \
    pexpect==4.8.0 \
    pickleshare==0.7.5 \
    prompt-toolkit==3.0.3 \
    ptyprocess==0.6.0 \
    pygments==2.5.2 \
    pyparsing==2.4.6 \
    pyqt5-sip==12.7.1 \
    pyqt5==5.14.1 \
    python-dateutil==2.8.1 \
    pytz==2019.3 \
    scipy==1.4.1 \
    six==1.14.0 \
    tqdm==4.43.0 \
    traitlets==4.3.3 \
    wcwidth==0.1.8

# clean the house
RUN apt-get autoremove -y && \
    rm /var/lib/apt/lists/* rm -rf /var/cache/apt/*