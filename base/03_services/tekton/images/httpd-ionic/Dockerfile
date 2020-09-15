FROM registry.access.redhat.com/ubi8-minimal

RUN microdnf install -y httpd && \
    microdnf -y clean all && \
    sed -i 's/Listen 80/Listen 8080/' /etc/httpd/conf/httpd.conf && \
    sed -i 's/User apache/User nobody/' /etc/httpd/conf/httpd.conf && \
    sed -i 's/Group apache/Group nobody/' /etc/httpd/conf/httpd.conf && \
    chmod -c -R a+rwX  /etc/httpd/conf /run/httpd /var/log/httpd 

COPY rewrite.conf /etc/httpd/conf.d/

ENV HTTPD_CONTAINER_SCRIPTS_PATH=/usr/share/container-scripts/httpd/ \
    HTTPD_APP_ROOT=${APP_ROOT} \
    HTTPD_CONFIGURATION_PATH=${APP_ROOT}/etc/httpd.d \
    HTTPD_MAIN_CONF_PATH=/etc/httpd/conf \
    HTTPD_MAIN_CONF_MODULES_D_PATH=/etc/httpd/conf.modules.d \
    HTTPD_MAIN_CONF_D_PATH=/etc/httpd/conf.d \
    HTTPD_VAR_RUN=/var/run/httpd \
    HTTPD_DATA_PATH=/var/www \
    HTTPD_DATA_ORIG_PATH=/var/www \
    HTTPD_LOG_PATH=/var/log/httpd

EXPOSE 8080

USER 1001

STOPSIGNAL SIGWINCH
#ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]