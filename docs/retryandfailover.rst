
Retry and Failover
=================================

The workflow on retry and failover:

- Send a request to the RPC node
- If the node returns an HTTP status between *400 and 600 or had a timeout, retry the request up to times.
- Sleep time between cycles has an exponential backoff.
- If the node still can't respond, switch tho next available node until exhausting the node list.
- If all nodes are down or giving errors, and the system is out of options, the original exception is raised.