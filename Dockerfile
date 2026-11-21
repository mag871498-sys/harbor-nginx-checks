FROM nginx:1.31.9-alpine@sha256:fb4658584bd9a916ffb6f6e365f97c25cfdb2923801f551ea08356e695f14ff7
COPY nginx/harbor.conf /etc/nginx/conf.d/default.conf
COPY web/ /usr/share/nginx/html/
