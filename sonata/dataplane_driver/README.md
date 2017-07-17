## Testing the Dataplane Driver

To test the dataplane driver, use the `dpd_test.py` script and the pickled queries in `dp_queries_clean.pickle`.

```shell
cd sonata
PYTHONPATH=$PYTHONPATH:$PWD python dataplane_driver/dpd_test.py dataplane_driver/dp_queries_clean.pickle
```