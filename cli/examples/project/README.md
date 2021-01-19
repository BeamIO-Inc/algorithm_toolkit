# ATK Example Algorithms

Example algorithms and algorithm chain for the Algorithm Toolkit.

# Docker

## Overview

* If you have not already, make sure you have the "atk" Docker image installed
* Instructions on how to do this can be found in the [main README](../../../README.md) near the bottom under Docker
* Here, we will be building a Docker image that was made specifically for this example project
* Our Docker image is built using the following custom [Dockerfile](Dockerfile)
* This Dockerfile does the following
  * Includes everything in the "atk" Docker image
  * Installs any necessary software the ATK project may need
  * Installs all the required python libraries for the project
  * Runs the ATK/flask project

## Building the example project Docker image

```shell
git clone https://github.com/BeamIO-Inc/algorithm_toolkit.git
cd algorithm_toolkit/cli/examples/project
docker build -t atk-example .
```

## Running the Docker image we just built (Creating a Docker container)

```shell
docker run -d -p 5000:5000 atk-example
```

* Now that we have created a Docker container from the image, you will be able to access the ATK development web server on your local machine using http://localhost:5000