BUILD_HOST=192.168.0.13:32000
NAME=jopmcp
TAG=$(shell git log -1 --pretty=%h)

pkg:
	echo "Tag: " ${TAG}
	echo ${NAME}:${TAG}
	docker build -t ${NAME}:${TAG} .
	-docker inspect "${NAME}:latest" > /dev/null 2>&1 || docker rmi ${NAME}:latest
	docker tag ${NAME}:${TAG} ${NAME}:latest
	docker tag ${NAME}:${TAG} ${BUILD_HOST}/${NAME}:${TAG}
	docker tag ${NAME}:${TAG} ${BUILD_HOST}/${NAME}:latest
	# docker push ${BUILD_HOST}/${NAME}:${TAG}
	# docker push ${BUILD_HOST}/${NAME}:latest
	# trivy image ${NAME}:${TAG}

install:
	uv sync

server:
	LOGGING_CONFIG=dev_logging.conf uv run python -m jopmcp.main

client:
	LOGGING_CONFIG=dev_logging.conf uv run python -m jopmcp.mcp_client
