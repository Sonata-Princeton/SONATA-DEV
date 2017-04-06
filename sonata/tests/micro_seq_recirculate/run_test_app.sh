#!/bin/bash

#NUMBER_OF_QUERIES_ARRAY=[1 10 20 30 40 50 60 70 80 90 100]
#P4_TYPES=['recirculate' 'sequential']

for queries in 1 10 20 30 40 50 60 70 80 90 100;
do
    for p4 in 'recirculate' 'sequential';
    do
        echo "##############################"$queries","$p4"##############################"
        CMD="sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD python sonata/tests/micro_seq_recirculate/test_app.py $queries $p4 && sudo sh cleanup.sh"
        echo $CMD
        `$CMD`
        sleep 5
        echo "##############################"$queries","$p4"##############################"
    done
done
