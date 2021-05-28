export DISPLAY=$(ip route|awk '/^default/{print $3}'):0.0
docker run --volume="$HOME/.Xauthority:/root/.Xauthority:rw" --env="DISPLAY=$DISPLAY" artefact.skatelescope.org/ska-tango-images/tango-pogo:9.6.31.2
