FROM ubuntu:24.04

COPY --chmod=440 etc/apt/sources.list /etc/apt/sources.list
RUN mv /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak

RUN apt-get -o Acquire::https::Verify-Peer=false update --yes \
    && apt-get -o Acquire::https::Verify-Peer=false install --no-install-recommends --yes ca-certificates \
    && DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::https::Verify-Peer=false install --no-install-recommends --yes \
        iputils-ping git gh python3 openssh-server curl wget \
        vim  htop iotop iftop net-tools build-essential python3-pip jq tree \
        ncdu unzip zip rsync nmap telnet supervisor tzdata \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && mkdir -p /run/sshd

COPY --chmod=640 etc/supervisor /etc/supervisor
COPY --chmod=750 init.sh /

CMD  ["/init.sh"]
