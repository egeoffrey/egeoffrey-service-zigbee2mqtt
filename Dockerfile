### EGEOFFREY ###

### define base image
## the SDK version to bind to has to be passed by the builder so to select the right base image
ARG SDK_VERSION
ARG ARCHITECTURE
FROM egeoffrey/egeoffrey-sdk-raspbian:${SDK_VERSION}-${ARCHITECTURE}

### copy files into the image
COPY . $WORKDIR
