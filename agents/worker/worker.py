import tapeagents
from rq.worker import SimpleWorker, Worker
from tools.rate_limiter import rate_limiter
import os
import time


class AgentWorker(Worker):
    def work(self, *args, **kwargs):
        from tools.rate_limiter import rate_limiter

        globals()["rate_limiter"] = rate_limiter
        super().work(*args, **kwargs)

    def fork_work_horse(self, job: "Job", queue: "Queue"):
        """Spawns a work horse to perform the actual work and passes it a job.
        This is where the `fork()` actually happens.

        Args:
            job (Job): The Job that will be ran
            queue (Queue): The queue
        """
        child_pid = os.fork()
        os.environ["RQ_WORKER_ID"] = self.name
        os.environ["RQ_JOB_ID"] = job.id
        if child_pid == 0:
            os.setpgrp()
            self.main_work_horse(job, queue)
            os._exit(0)  # just in case
        else:
            from tools.rate_limiter import rate_limiter

            globals()["rate_limiter"] = rate_limiter
            self._horse_pid = child_pid
            self.procline("Forked {0} at {1}".format(child_pid, time.time()))
