FROM lsiobase/alpine
LABEL maintainer halfwalker

# package version
# (stable-download or testing-download)
ARG NZBGET_BRANCH="testing-download"

# install packages
RUN \
 apk add --no-cache \
	curl \
	p7zip \
	python \
    unrar \
	wget

# Install rar 5.40
# Missing libraries in lsiobase/alpline dangit
# ADD rarlinux-x64-5.4.0.tar.gz /tmp
# RUN \
#   mv /tmp/rar/rar /tmp/rar/unrar /usr/bin && \
#   mv /tmp/rar/default.sfx /usr/lib && \
#   mv /tmp/rar/rarfiles.lst /etc

# install nzbget
RUN \
 curl -o \
 /tmp/json -L \
	http://nzbget.net/info/nzbget-version-linux.json && \
 NZBGET_VERSION=$(grep "${NZBGET_BRANCH}" /tmp/json  | cut -d '"' -f 4) && \
 curl -o \
 /tmp/nzbget.run -L \
	"${NZBGET_VERSION}" && \
 sh /tmp/nzbget.run --destdir /app && \

# cleanup
 rm -rf \
	/tmp/*

# add local files
COPY root/ /

# Copy scripts
COPY scripts/ /app/scripts/

# ports and volumes
VOLUME /config /downloads
EXPOSE 6789
