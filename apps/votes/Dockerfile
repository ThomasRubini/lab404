FROM dhi.io/golang:1.26-dev@sha256:6911531f7408ac264734be729f8a230c207653d049cd03b2454ae9466a18e27c AS builder

USER 1000:1000
WORKDIR /tmp/src
ENV GOCACHE=/tmp/go-build \
    GOMODCACHE=/tmp/go-mod
COPY go.mod go.sum ./
RUN go mod download
COPY . .
ARG TARGETOS
ARG TARGETARCH
RUN CGO_ENABLED=0 GOOS="${TARGETOS}" GOARCH="${TARGETARCH}" \
    go build -o /tmp/votes .

FROM scratch

COPY --from=builder --chown=65532:65532 /tmp/votes /usr/bin/votes
USER 65532:65532
EXPOSE 8081
ENTRYPOINT ["/usr/bin/votes"]
