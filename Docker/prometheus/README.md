# Grafana Dashboard Fixes — cAdvisor / node_exporter
Import dashboard: 10566 - Docker Container & Host Metrics from both cAdvisor and Node Exporter 

Common issues when importing community "Docker and OS metrics" style dashboards against a Prometheus + cAdvisor + node_exporter stack.

## Job / Node dropdown only shows one option (or "No data" on host panels)

**Symptom:** Container-level panels work, but host-level panels (CPU, Memory, Uptime, Load1, Disk) show "No data". The `Job` and `Node` dropdown filters only list `cadvisor`, never `node-exporter`.

**Cause:** The dashboard's `Job`/`Node` template variables query label values from a metric that's only exported by cAdvisor (e.g. `cadvisor_version_info`). Since node_exporter doesn't expose that metric, its instance never appears as a dropdown option — even though it's being scraped correctly.

**Fix:** Dashboard settings → Variables → select the variable → Open variable editor → change **Metric** field from the cadvisor-specific metric to:

```
up
```

`up` is exposed by every Prometheus target regardless of job, so both `cadvisor` and `node-exporter` instances populate correctly. Repeat for both `Job` and `Node` variables.

## Containers panel stuck at N/A

**Symptom:** After fixing the Node/Job variables, all panels work except a "Containers" count panel.

**Query:**
```
count(rate(container_last_seen{id=~"/docker/.*", instance=~"$node"}[5m]))
```

**Cause:** The `id=~"/docker/.*"` filter assumes the older **cgroupfs** cgroup driver, where container paths look like `/docker/<hash>`. Systems using the **systemd** cgroup driver instead produce paths like `/system.slice/docker-<hash>.scope`, which the regex doesn't match.

**Fix:** Update the regex to match both conventions:

```
id=~"/docker/.*|/system.slice/docker-.*.scope"
```

## Debugging checklist

1. Check `http://<prometheus-host>:9090/targets` — confirm the job is `UP`
2. Test the raw metric in `http://<prometheus-host>:9090/graph` — confirms scraping/data exists, isolating the problem to Grafana's query/variable config
3. Check the dashboard's template variables (Dashboard settings → Variables) — a metric scoped to one job is the most common cause of missing dropdown options