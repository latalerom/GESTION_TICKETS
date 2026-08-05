FROM nginx:1.27-alpine

# El frontend queda como un servicio independiente: Nginx sirve HTML/CSS/JS
# y tambien actua como proxy para que fetch('/api/...') siga funcionando.
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/ /usr/share/nginx/html/
