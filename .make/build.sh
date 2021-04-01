#!/bin/bash

if [ -z "$PROJECT" ]
then
  NAME=$(basename $(pwd))
else
  NAME=$PROJECT
fi

if [ -z "$DOCKER_REGISTRY_HOST" ]
then
DOCKER_REGISTRY_HOST=nexus.engageska-portugal.pt
fi

if [ -z "$DOCKER_REGISTRY_USER" ]
then
DOCKER_REGISTRY_USER=ska-tango-images
fi

if [ -z "$DOCKER_BUILD_CONTEXT" ]
then
DOCKER_BUILD_CONTEXT=.
fi

if [ -z "$DOCKER_FILE_PATH" ]
then
DOCKER_FILE_PATH=Dockerfile
fi

IMAGE=$DOCKER_REGISTRY_HOST/$DOCKER_REGISTRY_USER/$NAME

if [ -z "$VERSION" ]
then
VERSION=$(awk -F= '/^release=/{print $2}' .release)
fi

if [ -z "$TAG" ]
then
TAG=$(awk -F= '/^tag/{print $2}' .release)
fi

while IFS='' read -r LINE || [ -n "${LINE}" ]; do
    if [[ $LINE == *"CI"* ]] && ![[ $LINE == *"MASKED"* ]]; then
        if [ -z "$LABELS" ]
        then
        LABELS='--label '${LINE}
        else
        LABELS=${LABELS}' --label '${LINE}
        fi
    fi
done <<< "$(printenv)"

docker build -t $IMAGE:$VERSION $LABELS $DOCKER_BUILD_CONTEXT -f $DOCKER_FILE_PATH 
DOCKER_MAJOR=$(docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f1) ; \
DOCKER_MINOR=$(docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f2) ; \
if [ $DOCKER_MAJOR -eq 1 ] && [ $DOCKER_MINOR -lt 10 ] 
then
    echo docker tag -f $IMAGE:$VERSION $IMAGE:latest
    docker tag -f $IMAGE:$VERSION $IMAGE:latest
else
    echo docker tag $IMAGE:$VERSION $IMAGE:latest
    docker tag $IMAGE:$VERSION $IMAGE:latest
fi

