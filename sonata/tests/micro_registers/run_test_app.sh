#!/bin/bash

#NUMBER_OF_QUERIES_ARRAY=[1 10 20 30 40 50 60 70 80 90 100]
#P4_TYPES=['recirculate' 'sequential']

for registers in 1 10 100 300 500 700 900;
do
    echo "##############################"$registers"##############################"
    CMD="sudo PYTHONPATH=$PYTHONPATH:/home/vagrant/bmv2/mininet:$PWD python sonata/tests/micro_registers/test_app.py $registers && sudo sh cleanup.sh"
    echo $CMD
#    `$CMD`
    echo "##############################"$registers"##############################"
done
