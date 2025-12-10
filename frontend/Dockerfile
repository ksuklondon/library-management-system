# Etap 1: Build (Vite + React)
FROM node:20-alpine AS builder

WORKDIR /app

# Kopiujemy zależności
COPY package*.json ./

# Instalujemy zależności
RUN npm install

# Kopiujemy pliki projektu (w tym .env)
COPY . .

# Tworzymy build produkcyjny – Vite przeczyta zmienne z .env
RUN npm run build

# Etap 2: Serwowanie przez nginx
FROM nginx:alpine

# Kopiujemy build do katalogu nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Otwieramy port (80)
EXPOSE 80

# Domyślna komenda nginx
CMD ["nginx", "-g", "daemon off;"]
