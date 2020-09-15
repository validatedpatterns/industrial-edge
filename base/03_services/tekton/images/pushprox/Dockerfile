FROM golang as builder
RUN git clone https://github.com/robustperception/pushprox.git && cd pushprox && make build


FROM registry.access.redhat.com/ubi8-minimal
COPY --from=builder /go/pushprox/pushprox-proxy /go/pushprox/pushprox-client .
EXPOSE 8080
ENTRYPOINT ["./pushprox-proxy"]
