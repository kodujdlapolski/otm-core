FROM python:2.7-stretch
COPY . /app/
WORKDIR /app
RUN mkdir -p /app/static_dir
RUN mkdir -p /app/media
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get update && apt-get install -y libproj-dev gdal-bin libfreetype6-dev python-pip nodejs npm
RUN npm install && npm install -g yarn
RUN yarn
RUN yarn run build
RUN pip install -r requirements.txt
RUN pip install -r dev-requirements.txt