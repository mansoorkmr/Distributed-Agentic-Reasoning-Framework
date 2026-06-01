import subprocess
import uuid

def submit_job(script_path):
    job_name = f"agent_{uuid.uuid4().hex[:6]}"

    command = [
        "sbatch",
        "--job-name", job_name,
        "hpc/job_scripts/agent_job.sh",
        script_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    return result.stdout.strip()
