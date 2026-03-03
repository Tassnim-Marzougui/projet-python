# ══════════════════════════════════════════════════
#  Stage 1 : Build React (Create React App)
# ══════════════════════════════════════════════════
FROM node:18-alpine AS builder

LABEL description="Nursery ML - React Frontend Builder"

WORKDIR /app

# Copier package.json en premier (cache Docker optimisé)
COPY frontend/package*.json ./

# Installer les dépendances
RUN npm ci --silent

# Copier le reste du code source
COPY frontend/ .

# Variables d'environnement pour le build
# L'API est proxifiée via Nginx donc on pointe vers /api
ENV REACT_APP_API_URL=/api
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false

# Build de production
RUN npm run build

# ══════════════════════════════════════════════════
#  Stage 2 : Servir avec Nginx (image légère)
# ══════════════════════════════════════════════════
FROM nginx:1.25-alpine

LABEL description="Nursery ML - React Frontend (Nginx)"

# Supprimer la config Nginx par défaut
RUN rm /etc/nginx/conf.d/default.conf

# Copier notre config Nginx personnalisée
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copier le build React depuis le stage précédent
COPY --from=builder /app/build /usr/share/nginx/html

# Port exposé
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:80 || exit 1

# Démarrer Nginx en foreground
CMD ["nginx", "-g", "daemon off;"]