all: help

# https://github.com/Halfwalker/docker-nzbget.git

# NZBGET app data stored here
CONFIG=/stuff/Downloads/NZBGet
# NZBGET main downloads location for Movies, TV etc
DOWNLOADS=/stuff/Downloads

NAME=docker-nzbget
USER=halfwalker
UID=$(shell id -u)
GID=$(shell id -g)
TZ=$(shell cat /etc/timezone)

update:	## Update docker-nzbget from github
		git pull --recurse-submodules
		wget "http://forum.nzbget.net/download/file.php?id=432" -O scripts/PasswordDetector.py
		wget "http://forum.nzbget.net/download/file.php?id=519" -O scripts/Move.py
		wget "http://forum.nzbget.net/download/file.php?id=586" -O /tmp/Completion.zip
		unzip /tmp/Completion.zip -d scripts
		rm /tmp/Completion.zip

build:	## Build the docker-nzbget container
		docker build . -t $(USER)/$(NAME)

run:	build ## Create and run the NZBGet container
		docker run \
			--rm -d --name $(NAME) \
			-p 6789:6789 \
			-e PUID=$(UID) -e PGID=$(GID) \
			-e TZ=$(TZ) \
			-v $(CONFIG):/config \
			-v $(DOWNLOADS):/downloads \
			$(USER)/$(NAME)

stop:	## Stop the running NZBGet container
		docker stop $(NAME)

shell:  ## Get a shell in the dovecot container
		docker exec -it $(NAME) /bin/bash

help:
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

