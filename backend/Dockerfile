FROM node:16-alpine
WORKDIR /app

COPY ./package.json /app

# RUN npm install
RUN npm install --save --legacy-peer-deps
# If you are building your code for production
# RUN npm ci --only=production

# Bundle app source
COPY . /app

EXPOSE 3000
CMD [ "node", "src/index.js" ]