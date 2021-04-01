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

label () {
  if [ -z "$LABELS" ]
  then
  LABELS='--label "'$1'"'
  else
  LABELS=${LABELS}' --label "'$1'"'
  fi
}


while IFS='' read -r LINE || [ -n "${LINE}" ]; do
    if [[ $LINE == *"CI_JOB_"* ]]; then
        label $LINE
    fi
    if [[ $LINE == *"CI_PIPELINE_"* ]]; then
        label $LINE
    fi
    if [[ $LINE == *"CI_PROJECT_"* ]]; then
        label $LINE
    fi
done <<< "$(printenv)"

echo docker build $DOCKER_BUILD_CONTEXT $LABELS -t $IMAGE:$VERSION -f $DOCKER_FILE_PATH 
docker build $DOCKER_BUILD_CONTEXT $LABELS -t $IMAGE:$VERSION -f $DOCKER_FILE_PATH 
DOCKER_MAJOR=$(docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f1)
DOCKER_MINOR=$(docker -v | sed -e 's/.*version //' -e 's/,.*//' | cut -d\. -f2)
if [ $DOCKER_MAJOR -eq 1 ] && [ $DOCKER_MINOR -lt 10 ] 
then
    echo docker tag -f $IMAGE:$VERSION $IMAGE:latest
    docker tag -f $IMAGE:$VERSION $IMAGE:latest
else
    echo docker tag $IMAGE:$VERSION $IMAGE:latest
    docker tag $IMAGE:$VERSION $IMAGE:latest
fi

