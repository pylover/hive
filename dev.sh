#! /usr/bin/env bash

gunicorn --reload --bind localhost:5555 wsgi:app

