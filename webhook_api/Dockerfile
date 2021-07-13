FROM node:alpine3.13

WORKDIR /app

COPY app.ts ./
COPY lib ./lib
COPY package*.json ./
COPY tsconfig.json ./

RUN npm install
RUN npm run build

EXPOSE 3200

CMD [ "npm", "start"]
