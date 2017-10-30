|#| Application Name  | Description|
| -|------------- | ------------- |
| 1|TCP New Conn | for which the number of newly opened TCP connections exceeds threshold.|
| 2|SSH Brute     | that receive similar-sized packets from more than threshold unique senders.|
| 3|SuperSpreader | that contact more than threshold unique destinations.|
| 4|Port Scan     | that send traffic over more than threshold destination ports.|
| 5|DDoS          |that receive traffic from more than threshold unique sources.|
| 6|Syn Flood     | for which the number of half-open TCP connections exceeds threshold Th. |
| 7|Completed Flow| for which the number of incomplete TCP connections exceeds threshold.|
| 8|Slowloris Attack | for which the average transfer rate per flow is below threshold.|
| 9|DNS Tunneling | for which new TCP connections are not created after DNS query.|
| 10|Zorro Attck | that receive “zorro” command after telnet brute force.|
| 11|Reflection DNS| that receive DNS response of type “RRSIG” from many unique senders without requests.|
