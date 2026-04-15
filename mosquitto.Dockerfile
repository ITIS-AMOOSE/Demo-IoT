FROM eclipse-mosquitto:2

# Copy configs vào image
COPY configs/acl.txt /mosquitto/config/acl.txt
COPY configs/mosquitto_open.conf /mosquitto/config/mosquitto_open.conf
COPY configs/mosquitto_auth.conf /mosquitto/config/mosquitto_auth.conf
COPY configs/mosquitto_tls.conf /mosquitto/config/mosquitto_tls.conf

# Tạo password file trực tiếp trong config dir
RUN mosquitto_passwd -b -c /mosquitto/config/passwords.txt sensor sensor123 && \
    mosquitto_passwd -b /mosquitto/config/passwords.txt dashboard dashboard123 && \
    chmod 644 /mosquitto/config/passwords.txt

# Reset entrypoint về mặc định
ENTRYPOINT ["/usr/sbin/mosquitto"]
CMD ["-c", "/mosquitto/config/mosquitto_open.conf"]
