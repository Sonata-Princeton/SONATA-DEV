#!/usr/bin/env bash

sudo simple_switch loss_query.json --log-file switch_log --log-flush --interface 11@m-veth-1 --interface 12@out-veth-2 &
sleep 2
simple_switch_CLI < slow_queue.txt
sudo ./controller.py
wait
#sudo ps -ef | grep simple_switch | grep -v grep | awk '{print $2}' | sudo xargs kill -9