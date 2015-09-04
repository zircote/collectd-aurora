collectd-aurora
---------------

An attempt to collect(d) Apache Aurora metrics.


# Use

```
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  Modulepath "/opt/collectd/lib/collectd/plugins/python"
  Import "aurora_scheduler"

  <Module aurora_scheduler>
    instance my1
    host "my1.aurora.server.com"
    port 8081
    path /vars
    verbose false
  </Module>
  <Module aurora_scheduler>
    instance my2
    host "my2.aurora.server.com"
    port 8081
    path /vars
    verbose false
  </Module>
  <Module aurora_scheduler>
    instance my3
    host "my3.aurora.server.com"
    port 8081
    ssl = true
    path /vars
    verbose false
  </Module>
</Plugin>
```
