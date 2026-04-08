# Job Queue

## Queue Status

```python
status = client.server_jobqueue_status()
print(f"State: {status['queue_state']}")
for job in status["queued_jobs"]:
    print(f"  {job['filename']} (id: {job['job_id']})")
```

## Adding Jobs

```python
# Add a single job
client.server_jobqueue_job(filenames=["model.gcode"])

# Add multiple jobs
client.server_jobqueue_job(filenames=[
    "model_1.gcode",
    "model_2.gcode",
    "model_1.gcode",  # Same file again for repeat
])

# Clear queue and add new jobs
client.server_jobqueue_job(filenames=["urgent.gcode"], reset=True)
```

## Queue Control

```python
client.server_jobqueue_start()   # Start processing the queue
client.server_jobqueue_pause()   # Pause (finish current, don't load next)
```

## Reorder

```python
# Jump a job to the front
client.server_jobqueue_jump(job_id="job-uuid-here")
```
