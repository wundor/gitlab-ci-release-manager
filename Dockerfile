FROM node:lts
WORKDIR /src
COPY package.json /src/
COPY package-lock.json /src/
COPY index.js /src/
RUN npm ci
ENTRYPOINT node index.js
