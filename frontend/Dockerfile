# Etap 1: Build (Vite + React)
FROM node:20-alpine AS builder

WORKDIR /app

# ⭐ DODAJ - Przyjmij argumenty z docker-compose
ARG VITE_AUTH_API_URL
ARG VITE_CATALOG_API_URL
ARG VITE_LOAN_API_URL

# ⭐ DODAJ - Ustaw jako zmienne środowiskowe
ENV VITE_AUTH_API_URL=$VITE_AUTH_API_URL
ENV VITE_CATALOG_API_URL=$VITE_CATALOG_API_URL
ENV VITE_LOAN_API_URL=$VITE_LOAN_API_URL

# Kopiujemy zależności
COPY package*.json ./

# Instalujemy zależności
RUN npm install

# Kopiujemy pliki projektu
COPY . .

# Tworzymy build produkcyjny – Vite użyje zmiennych ENV
RUN npm run build

# Etap 2: Serwowanie przez nginx
FROM nginx:alpine

# Kopiujemy build do katalogu nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Otwieramy port (80)
EXPOSE 80

# Domyślna komenda nginx
CMD ["nginx", "-g", "daemon off;"]
