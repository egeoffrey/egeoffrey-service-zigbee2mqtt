# egeoffrey-service-zigbee2mqtt

This is an eGeoffrey service package.

## Description

Integrate with Zigbee2mqtt by connecting to the same mqtt broker Zigbee2mqtt is publishing devices data.

## Install

To install this package, run the following command from within your eGeoffrey installation directory:
```
egeoffrey-cli install egeoffrey-service-zigbee2mqtt
```
After the installation, remember to run also `egeoffrey-cli start` to ensure the Docker image of the package is effectively downloaded and started.
To validate the installation, go and visit the *'eGeoffrey Admin'* / *'Packages'* page of your eGeoffrey instance. All the modules, default configuration files and out-of-the-box contents if any will be automatically deployed and made available.
## Content

The following modules are included in this package.

For each module, if requiring a configuration file to start, its settings will be listed under *'Module configuration'*. Additionally, if the module is a service, the configuration expected to be provided by each registered sensor associated to the service is listed under *'Service configuration'*.

To configure each module included in this package, once started, click on the *'Edit Configuration'* button on the *'eGeoffrey Admin'* / *'Modules'* page of your eGeoffrey instance.
- **service/zigbee2mqtt**: interact with sensors through a mqtt broker
  - Module configuration:
    - *hostname**: the MQTT broker hostname to connect to (e.g. egeoffrey-gateway)
    - *port**: the port of the MQTT broker (e.g. 1883)
    - *username*: the username for authenticating against the mqtt broker (e.g. username)
    - *password*: the password for authenticating against the mqtt broker (e.g. password)
    - *base_topic**: zigbee2mqtt base topic (e.g. zigbee2mqtt)
  - Service configuration:
    - Mode 'push':
      - *device_id**: the friendly name assiged to the device (e.g. 0x00158d000346c0b3)
      - *key**: the key of the payload whose measure has to be extracted (e.g. temperature)
      - *filter*: filter in only a subset of data based on conditions provided in the format key1=value1&key2=value2 (e.g. action=rotate_right)
    - Mode 'actuator':
      - *device_id**: the friendly name assiged to the device (e.g. 0x00158d000346c0b3)
      - *key**: set the value to the following attribute (e.g. state)

## Contribute

If you are the author of this package, simply clone the repository, apply any change you would need and run the following command from within this package's directory to commit your changes and automatically push them to Github:
```
egeoffrey-cli commit "<comment>"
```
After taking this action, remember you still need to build (see below) the package (e.g. the Docker image) to make it available for installation.

If you are a user willing to contribute to somebody's else package, submit your PR (Pull Request); the author will take care of validating your contributation, merging the new content and building a new version.

## Build

Building is required only if you are the author of the package. To build a Docker image and automatically push it to [Docker Hub](https://hub.docker.com/r/egeoffrey/egeoffrey-service-zigbee2mqtt), run the following command from within this package's directory:
```
egeoffrey-cli build egeoffrey-service-zigbee2mqtt
```

## Uninstall

To uninstall this package, run the following command from within your eGeoffrey installation directory:
```
egeoffrey-cli uninstall egeoffrey-service-zigbee2mqtt
```
Remember to run also `egeoffrey-cli start` to ensure the changes are correctly applied.
## Tags

The following tags are associated to this package:
```
service mqtt zigbee
```

## Version

The version of this egeoffrey-service-zigbee2mqtt is 1.0-4 on the master branch.
