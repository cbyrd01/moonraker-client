"""API endpoints for Jobs operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class JobsMixin:
    """Synchronous jobs API methods."""

    def server_jobqueue_status(self) -> Any:
        """Get job queue status

        Retrieves the current state of the job queue.

        JSON-RPC method: server.job_queue.status
        """
        return self._request("GET", "/server/job_queue/status")

    def server_jobqueue_job(self, filenames: list[str], reset: bool = False) -> Any:
        """Enqueue a job

        Adds a job, or an array of jobs, to the end of the job queue.  The same
        filename may be specified multiple times to queue a job that repeats.
        When multiple jobs are specified they will be enqueued in the order they
        are received.
        
        **Note:** The request will be aborted and return an error if any of the supplied
        files do not exist.
        
        **Note:** If it isn't possible for your client to pass parameters in the body
        of the request as a json object, they can be added to the query string
        as shown below:
        
        ```{.http .apirequest title="HTTP Request"}
        POST /server/job_queue/job?filenames=job1.gcode,job2.gcode,subdir/job3.gcode
        ```
        
        Multiple jobs should be comma separated as shown above.

        Args:
            filenames: An array of filenames of jobs to add to the queue. The file names should be path
            reset: When set to `true` the job queue will be cleared prior to adding the requested j (optional)

        JSON-RPC method: server.job_queue.post_job
        """
        body: dict[str, Any] = {}
        body["filenames"] = filenames
        if reset is not None:
            body["reset"] = reset
        return self._request("POST", "/server/job_queue/job", json=body)

    def server_jobqueue_pause(self) -> Any:
        """Pause the job queue

        Sets the job queue state to "pause", which prevents the next job
        in the queue from loading after an job in progress is complete.
        If the queue is paused while the queue is in the `loading` state
        the load will be aborted.

        JSON-RPC method: server.job_queue.pause
        """
        return self._request("POST", "/server/job_queue/pause")

    def server_jobqueue_start(self) -> Any:
        """Start the job queue

        Starts the job queue.  If Klipper is ready to start a print the next
        job in the queue will be loaded.  Otherwise the queue will be put
        into the "ready" state, where the job will be loaded after the current
        job completes.

        JSON-RPC method: server.job_queue.start
        """
        return self._request("POST", "/server/job_queue/start")

    def server_jobqueue_jump(self, job_id: str) -> Any:
        """Perform a Queue Jump

        Jumps a job to the front of the queue.

        Args:
            job_id: The `job_id` of the job to jump to the. front of the queue.

        JSON-RPC method: server.job_queue.jump
        """
        body: dict[str, Any] = {}
        body["job_id"] = job_id
        return self._request("POST", "/server/job_queue/jump", json=body)


class AsyncJobsMixin:
    """Asynchronous jobs API methods."""

    async def server_jobqueue_status(self) -> Any:
        """Get job queue status

        Retrieves the current state of the job queue.

        JSON-RPC method: server.job_queue.status
        """
        return await self._request("GET", "/server/job_queue/status")

    async def server_jobqueue_job(self, filenames: list[str], reset: bool = False) -> Any:
        """Enqueue a job

        Adds a job, or an array of jobs, to the end of the job queue.  The same
        filename may be specified multiple times to queue a job that repeats.
        When multiple jobs are specified they will be enqueued in the order they
        are received.
        
        **Note:** The request will be aborted and return an error if any of the supplied
        files do not exist.
        
        **Note:** If it isn't possible for your client to pass parameters in the body
        of the request as a json object, they can be added to the query string
        as shown below:
        
        ```{.http .apirequest title="HTTP Request"}
        POST /server/job_queue/job?filenames=job1.gcode,job2.gcode,subdir/job3.gcode
        ```
        
        Multiple jobs should be comma separated as shown above.

        Args:
            filenames: An array of filenames of jobs to add to the queue. The file names should be path
            reset: When set to `true` the job queue will be cleared prior to adding the requested j (optional)

        JSON-RPC method: server.job_queue.post_job
        """
        body: dict[str, Any] = {}
        body["filenames"] = filenames
        if reset is not None:
            body["reset"] = reset
        return await self._request("POST", "/server/job_queue/job", json=body)

    async def server_jobqueue_pause(self) -> Any:
        """Pause the job queue

        Sets the job queue state to "pause", which prevents the next job
        in the queue from loading after an job in progress is complete.
        If the queue is paused while the queue is in the `loading` state
        the load will be aborted.

        JSON-RPC method: server.job_queue.pause
        """
        return await self._request("POST", "/server/job_queue/pause")

    async def server_jobqueue_start(self) -> Any:
        """Start the job queue

        Starts the job queue.  If Klipper is ready to start a print the next
        job in the queue will be loaded.  Otherwise the queue will be put
        into the "ready" state, where the job will be loaded after the current
        job completes.

        JSON-RPC method: server.job_queue.start
        """
        return await self._request("POST", "/server/job_queue/start")

    async def server_jobqueue_jump(self, job_id: str) -> Any:
        """Perform a Queue Jump

        Jumps a job to the front of the queue.

        Args:
            job_id: The `job_id` of the job to jump to the. front of the queue.

        JSON-RPC method: server.job_queue.jump
        """
        body: dict[str, Any] = {}
        body["job_id"] = job_id
        return await self._request("POST", "/server/job_queue/jump", json=body)
