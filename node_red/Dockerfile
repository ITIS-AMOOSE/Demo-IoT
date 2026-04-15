FROM nodered/node-red:latest

# Cài node-red-dashboard
RUN npm install node-red-dashboard

# Copy settings (tắt mã hóa credentials)
COPY settings.js /data/settings.js

# Copy credentials (username/password cho MQTT broker)
COPY flows_cred.json /data/flows_cred.json
