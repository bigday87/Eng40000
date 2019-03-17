#!/bin/bash
sleep 5
sudo systemctl start grafana-server 
sleep 5
while true; do python /home/pi/infl.py -db=energy -sn test1 && break; done

	
