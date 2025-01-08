FROM node:14

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
