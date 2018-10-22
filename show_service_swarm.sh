#!/usr/bin/env bash
echo "Printing 'docker service ls | grep tweaker':"
docker service ls | grep tweaker
echo ""
echo "Printing 'docker stack ps tweaker':"
docker stack ps tweaker
