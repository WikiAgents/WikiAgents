source activate base
conda activate agents
rq worker -w 'worker.worker.AgentWorker' --url redis://redis:6379 agents-queue tools-queue
