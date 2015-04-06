collectd-aurora
---------------

An attempt to collect(d) Apache Aurora metrics.


# Use

```
<LoadPlugin python>
  Globals true
</LoadPlugin>

<Plugin python>
  ModulePath "/opt/collectd/lib/collectd/plugins/python"
  Import "aurora_scheduler"

  <Module aurora_scheduler>
    Instance my1
    Host "my1.aurora.server.com"
    Port 8081
    Scheme http
    Path /vars
    Verbose false
  </Module>
  <Module aurora_scheduler>
    Instance my2
    Host "my2.aurora.server.com"
    Port 8081
    Scheme http
    Path /vars
    Verbose false
  </Module>
  <Module aurora_scheduler>
    Instance my3
    Host "my3.aurora.server.com"
    Port 8081
    Scheme http
    Path /vars
    Verbose false
  </Module>
</Plugin>
```
