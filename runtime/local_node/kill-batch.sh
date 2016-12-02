ps -ef | grep local_detection | grep -v grep | awk '{print $2}' | xargs kill -9
