FROM python:3.6.9

ENV TZ="Europe/Warsaw"
RUN date

# Disable setuid / setgid binaries - for security
# RUN find / -perm /6000 -type f -exec chmod a-s {} \; || true

# Install firefox to run selenium
RUN apt-get update && apt-get install -y \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget \
    xvfb

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

COPY requirements.txt /
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /requirements.txt

# Set up a new user to run the services
RUN useradd -ms /bin/bash trai_app
USER trai_app
ENV APP_PATH /home/trai_app

# Copy project files to user directory
RUN mkdir -p $APP_PATH
COPY --chown=trai_app:trai_app . $APP_PATH
WORKDIR $APP_PATH
RUN chmod +x ./start.sh

ENTRYPOINT ["./start.sh"]
