import os
import parsl
from pathlib import Path
from parsl import bash_app, File
from parsl.executors import HighThroughputExecutor
from parsl.providers import PBSProProvider
from parsl.config import Config
from parsl.launchers import SingleNodeLauncher

# ---------- USER VARIABLES ----------
account     = 'a_surface' # account to charge
num_nodes   = 2           # max number of nodes to use
walltime    = '1:00:00'   # job length
fdmnes_exe  = '/home/vferreiragrizzi/parallel_fdmnes/mpirun_fdmnes'
num_cores   = int(os.environ.get('PBS_NP', '128'))
# ------------------------------------

root_dir = Path(os.environ.get('PBS_O_WORKDIR', Path.cwd()))
if root_dir.name == 'fdmnes_batch_runs':
    root_dir = root_dir.parent
runs_dir = root_dir / 'fdmnes_batch_runs'

if runs_dir.name != 'fdmnes_batch_runs':
    raise ValueError('You must submit the job or run the code from "fdmnes_batch_runs" or its parent directory!!')

@bash_app
def run_fdmnes(run_dir, ncores, exe, stdout=None, stderr=None, outputs=None, cwd=None):
    run_cmd = [f'cd "{run_dir}"',
               f'"{exe}" -np {ncores}']
    return "\n".join(run_cmd)

def is_calc_done(run_dir: Path) -> bool:
    """Return True if a successful _conv.txt exists and is non‑empty."""
    conv = next(run_dir.glob('*_conv.txt'), None)
    return conv is not None and conv.stat().st_size > 1024

run_dirs = [d for d in runs_dir.glob('run_*') if d.is_dir() and not is_calc_done(d)]
if not run_dirs:
    print('All calcs are done already!!')
    quit()

# initializing the task dispatcher
htex = HighThroughputExecutor(
    label='htex',
    max_workers_per_node=1, # each worker is a process; this controls the max number of processes (jobs/runs) per node
    cores_per_worker=num_cores, # each worker gets all the cores in the node since num_cores = os.environ.get('PBS_NP')
    provider=PBSProProvider(
        account=account, # account to charge the used resources
        nodes_per_block=1, # block is the smallest unit of compute allocation, here 1 block = 1 node
        cpus_per_node=num_cores, # number of cores to use per node
        init_blocks=min(num_nodes, len(run_dirs)), # ensures that we don't use more nodes than needed
        max_blocks=num_nodes, # maximum number of blocks Parsl is allowed to allocate (#used_nodes = nodes_per_blocks * max_blocks)
        walltime=walltime, # maximum time per block/job
        scheduler_options='#PBS -N FDMNES_parsl', # custom PBS headers
        worker_init="""
            source ~/miniconda/etc/profile.d/conda.sh
            conda activate qc_env
            export OMP_NUM_THREADS=1
        """,
        launcher=SingleNodeLauncher(), # tells Parsl to give the whole node to one worker, i.e. worker is launched once per node.
    ),
)

parsl.load(Config(executors=[htex], retries=2)) # starts Parsl using the provided executor

futures = [] # a future object is a computation that will be completed later
for curr_dir in run_dirs:
    futures.append(
        run_fdmnes(
            run_dir=str(curr_dir),
            ncores=num_cores,
            exe=fdmnes_exe, # exe command to run the desired program
            cwd=str(curr_dir),
            stdout=str(curr_dir / 'fdmnes_stdout.txt'),
            stderr=str(curr_dir / 'fdmnes_stderr.txt'),
            outputs=[File(str(curr_dir / '_conv.txt'))] # Parls knows the task is done when '_conv.txt' is written
        )   # Bottom 3 params are Parsl specific. They aren't passed to the function but handled by Parsl internally
    )

print(f'Submitted {len(futures)} runs to Parsl')

# Wait until all future tasks are complete before proceeding, i.e. blocks further execution of the script
for fut in futures:
    fut.result()

print('All runs finished')
parsl.clear() # shutdows Parsl: free resources, terminate any idle workers, clears internal caches, etc.

# We run Parsl on a main/driver node for the longest possible walltime. This node dynamically launches worker blocks
# (in this case each worker block is 1 node, and a maximum of `num_nodes` blocks can be launched). Note that if this
# main node job dies due to walltime limits, the HTEX workers can no longer communicate and shut down (this can be
# after task completion if no communication is need). This is by design since Parsl is meant to manage the full job
# lifecycle, i.e. its workers are not meant to persist beyond the life of the driver. But it is not a problem that
# unfinished jobs are killed because we built a mechanism to check job completion upon restart.

# Calling a function decorated with @bash_app (run_fdmnes in our case) makes Parsl launches a series of events. Parsl
# doesn't run the command immediately; instead it returns a Future object representing a task to be run later. However,
# calling the @bash_app function triggers a chain of events:
# 1) Block allocation -> Parsl submits PBS jobs via the PBSProProvider (here 1 block = 1 node). Up to `max_blocks`
#                        can be submited based on demand. The commands inside `worker_init` are appended after the
#                        directives (#PBS headers) in the PBS submission file.
# 2) Launch workers -> Since we used SingleNodeLauncher, a single worker is launched per block. The main Parsl process
#                      opens a socket and remote workers connect to it in order to request tasks and send back results.
#                      Tasks are distributed to workers based on a queue. As a side node, the workers communicates with
#                      the main Parsl process using ZeroMQ sockets over TCP/IP. The main Parsl process opens a ZeroMQ
#                      server socket to which remote workers on computing nodes connect using ZeroMQ client sockets.
#                      This allows these two processes running on different nodes to exchange information and send data
#                      back and forth.
# 3) Task dispatch -> The main script serializes the @bash_app decorated task containing a shell command and sends it
#                     to an available worker via the ZeroMQ protocol. This worker deserializes it and runs the command.
#                     Parsl tracks the task completion via the `outputs` list specified in the @bash_app function. If
#                     we don't use `outputs` Parsl relies solely on the exit code, i.e. if the shell command in the
#                     @bash_app function returns 0 it is a success but if returns a non-zero exit code it is a failure.
#                     After the task finishes, the worker sends back result metadata (exit code, output, logs, etc.)
#                     OBS1: Note that the task/function must be serialized (transformed into a stream of bytes) because
#                           the worker in a remote node doesn't have access to our main Python process, nor it can call
#                           that function directly. Thus, the task must be serialized, sent to a worker, deserialized,
#                           and then executed.
