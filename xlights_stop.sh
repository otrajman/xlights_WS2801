#!/bin/sh
sudo kill -9 $(ps aux | grep lights.py | grep -v grep | awk '{print $2}')
