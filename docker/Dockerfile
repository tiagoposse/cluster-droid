ARG VAULT_VERSION

FROM vault:${VAULT_VERSION} as vault

FROM python:3.9-slim

COPY --from=vault /bin/vault /usr/local/bin

ARG ARCH=arm64
ARG HELM_VERSION
ARG KUBECTL_VERSION

ENV PYTHONBUFFERED=1

RUN apt update && apt install -y curl vim

RUN curl -LO https://get.helm.sh/helm-v${HELM_VERSION}-linux-${ARCH}.tar.gz && \
    tar -xzvf helm-v${HELM_VERSION}-linux-${ARCH}.tar.gz && rm helm-v$HELM_VERSION-linux-${ARCH}.tar.gz && \ 
    chmod +x linux-${ARCH}/helm && mv linux-${ARCH}/helm /usr/local/bin/helm && rm -rf linux-${ARCH}

RUN curl -LO "https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/${ARCH}/kubectl" && \
    chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl

COPY app/requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY app/*.py app/.appargs.yml /app/

ENTRYPOINT [ "python", "/app/main.py" ]