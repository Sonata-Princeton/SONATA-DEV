#!/bin/bash
sudo ./cleanup.sh

sudo $SPARK_HOME/bin/spark-submit sonata/examples/"$1"/test_app.py