FROM python:3.9.7

ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.29.0
ENV FIREFOX_VER 87.0
ENV RUNTIME_ENV DOCKER

RUN apt-get update \
   && apt-get upgrade -y \
   && apt-get install -y \
       firefox-esr

# Add latest Firefox
RUN apt-get install -y \
       libx11-xcb1 \
       libdbus-glib-1-2 \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox

# Add geckodriver
RUN curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/

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
