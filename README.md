# hive

[![Build Status](https://travis-ci.org/pylover/hive.svg?branch=master)](https://travis-ci.org/pylover/hive)
[![Coverage Status](https://coveralls.io/repos/github/pylover/hive/badge.svg?branch=master)](https://coveralls.io/github/pylover/hive?branch=master)

A set of REST APIs to create shared lists which can manipulated by anyone.


### Server


#### Installation

```bash
pip install -e .
hive db create -m
```


#### Quickstart

```bash
./dev.sh
```


### Ubuntu

There is an installation script to install configure the systemd script and
appropriate postgresql db.

Take a look inside and if you know what you the doing, then run the script as
root!

```bash
sudo ./install-server.sh
```

### Run tests


```bash
pip install requirements-dev.txt
pytest
```


### Client

Checkout https://github.com/pylover/bee

