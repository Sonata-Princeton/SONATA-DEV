#!/usr/bin/env bash
sudo ps -ef | grep simple_switch | grep -v grep | awk '{print $2}' | sudo xargs kill -9
sudo ps -ef | grep controller | grep -v grep | awk '{print $2}' | sudo xargs kill -9
sudo ps -ef | grep setup | grep -v grep | awk '{print $2}' | sudo xargs kill -9