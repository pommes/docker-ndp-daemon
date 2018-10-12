# docker-ndp-daemon
> Release v1-beta.1

Small python daemon that gives new started docker containers IPv6 internet connectivity by automatically adding their IPv6 addresses to the NDP proxy table.

## The situation
If you enable IPv6 on your Docker configuration you maybe have trouble with connecting your containers to the internet. [This article](https://docs.docker.com/v17.09/engine/userguide/networking/default_network/ipv6/) describes one way to achieve this with **Using NDP proxying**. The problem is that for IPv6's *NDP* every IP that should be proxied must be added to the proxy table. It is not possible to register an IP range like with IPv4's *ARP*.

## What docker-ndp-daemon does
*docker-ndp-daemon* watches [Dockers Event API](https://docs.docker.com/engine/api/v1.24/). If a container starts and connects to the network *docker-ndp-daemon* get's called, fetches the containers IPv6 address and adds it to the IPv6 NDP proxy table.
Now traffic from or to this IPv6 address is routed over the *network interface* that is the *Internet gateway*.

## Requirements
1. Tested with Python 3.6.6
2. The `docker` Python module (sudo install with `pip3 install docker`).
3. A user which can `sudo` to *root* without entering password.

## Installation
1. Download or clone *docker-ndp-daemon* from this repository.
2. Change settings in `dnd.ini`. Normally only the `gateway` has to be changed (Default: `eth0`). Set this to your hosts internet gatway network interface. If your docker socket differs from `/var/run/docker.sock` you can change this setting too.

Alternatively you can run the daemon as a docker container as well. You can use [this simple Dockerfile](./Dockerfile) as a template.

## Startup
`cd <download-dir>/app && python3 main.py`

It is necessary to *cd* into the `<download-dir>/app` directory first so that *docker-ndp-proxy* can find its configuration file `dnd.ini`.

## Log Output
After startup the logfile is printed to `STDOUT`:

```log
01:  2018-10-11 17:34:48,836 - daemon.events - INFO - Connecting ...
02:  2018-10-11 17:34:48,837 - daemon.ndp - INFO - Activating IPv6 ndp proxy on 'eth0' ...
03:  2018-10-11 17:34:48,864 - daemon.ndp - INFO - Adding all runnning containers to IPv6 ndp proxy...
04:  2018-10-11 17:34:49,034 - daemon.ndp - INFO - Ignoring container 'ipv6-enabler'. It has no IPv6 address.
05:  2018-10-11 17:34:49,123 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'mariadb': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::5 dev eth0'
06:  2018-10-11 17:34:49,170 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'sensu-monitor': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::12 dev eth0'
07:  2018-10-11 17:34:49,221 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'dokuwiki': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::16 dev eth0'
08:  2018-10-11 17:34:49,360 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'mail': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::15 dev eth0'
09:  2018-10-11 17:34:49,687 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'gitlab': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::8 dev eth0'
10:  2018-10-11 17:34:49,937 - daemon.events - INFO - Listening for Events ...
11:  2018-10-11 18:01:02,437 - daemon.ndp - INFO - Setting IPv6 ndp proxy for container 'backup': 'sudo ip -6 neigh add proxy 2a02:xxxx:yyyy:zzzz:d::17 dev eth0'
```

* Line **01**: *dnd* is connecting to the Docker API.
* Line **02**: *dnd* is activating *IPv6 NDP proxying* on the networking stack.
* Line **03**: From here to line **09** *dnd* is adding the IPv6 addresses of all currently running containers to the NDP proxy table.
* Line **10**: Startup phase is over. Now *dnd* is waiting for new *network connection events* from docker.
* Line **11**: *dnd* was informed that the container *backup* was just connected to the network and adds it's IPv6 address to the NDP proxy table.
