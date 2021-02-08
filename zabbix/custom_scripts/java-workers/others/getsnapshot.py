#!/usr/bin/python3
from datadog import initialize, api
import time

options = {
    'api_key': '',
    'app_key': ''
}

initialize(**options)

# Take a graph snapshot
end = int(time.time())
start = end - (2880 * 60)
reply = api.Graph.create(
    graph_def='{ \
       "viz": "timeseries", \
       "status": "done", \
       "requests": [{"q": "worker.dispatcher.task.timeout{env:production, queue:content} by {queue}.as_count()","type": "bars","style": {"palette": "dog_classic","type": "solid", \
        "width": "normal"}, \
        "conditional_formats": [], \
        "aggregator": "avg"}], \
        "autoscale": true}',
    start=start,
    end=end
)
print(reply)