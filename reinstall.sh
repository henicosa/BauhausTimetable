#!/bin/bash
docker stop bauhausbot
docker rm bauhausbot
git pull
sh ./install.sh
sh ./start.sh