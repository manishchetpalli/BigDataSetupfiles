import requests
import sys
import logging
import time

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("flink_terminate.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Define Flink cluster endpoints
FLINK_CLUSTERS = {

    "ajiob2b01": "http://IP.IP131.192:32000/ajiob2b01",
    "ajiob2b02": "http://IP.IP131.192:32000/ajiob2b02",
    "ajiob2c01": "http://IP.IP131.192:32000/ajiob2c01",
    "ajiob2c02": "http://IP.IP131.192:32000/ajiob2c02",
    "ajiob2c03": "http://IP.IP131.192:32000/ajiob2c03",
    "fusion": "http://IP.IP131.192:32000/fusion",
    "fusion02": "http://IP.IP131.192:32000/fusion02",
    "fusion03": "http://IP.IP131.192:32000/fusion03",
    "jiomart01": "http://IP.IP131.192:32000/jiomart01",
    "jiomart02": "http://IP.IP131.192:32000/jiomart02",
    "ros01": "http://IP.IP131.192:32000/ros01",
    "ros02": "http://IP.IP131.192:32000/ros02",
    "rp2": "http://IP.IP131.192:32000/rp2",
    "abcr3p19": "http://IP.IP131.192:32000/abcr3p19",
    "abcr3p22": "http://IP.IP131.192:32000/abcr3p22",
    "abcr3p33": "http://IP.IP131.192:32000/abcr3p33",
    "abcr3p44": "http://IP.IP131.192:32000/abcr3p44",
    "abcr3p52": "http://IP.IP131.192:32000/abcr3p52",
    "abcr3p51": "http://IP.IP131.192:32000/abcr3p51",
    "abcr3p54": "http://IP.IP131.192:32000/abcr3p54"
    }
        

# Authentication credentials
USERNAME = "dlkadmin"
PASSWORD = "dlkadmin#321"
AUTH = (USERNAME, PASSWORD)

def get_job_status(cluster_url, job_id):
    """Check job status."""
    job_url = f"{cluster_url}/jobs/{job_id}"
    try:
        response = requests.get(job_url, auth=AUTH, timeout=10)
        if response.status_code == 200:
            return response.json().get("status", "UNKNOWN")
    except requests.RequestException as e:
        logger.error(f"❌ Error fetching job status: {e}")
    return "UNKNOWN"

def get_job_name(cluster_url, job_id):
    """Fetch job name using job ID"""
    job_url = f"{cluster_url}/jobs/{job_id}"
    try:
        response = requests.get(job_url, auth=AUTH, timeout=10)
        if response.status_code == 200:
            return response.json().get("name", "Unknown")
    except requests.RequestException as e:
        logger.error(f"❌ Error fetching job details for Job ID {job_id}: {e}")
    return "Unknown"

def terminate_flink_job(cluster_name, job_name):
    """Terminate a specific Flink job by name and confirm termination."""
    if cluster_name not in FLINK_CLUSTERS:
        logger.error(f"❌ Invalid cluster '{cluster_name}'. Check configuration.")
        return

    cluster_url = FLINK_CLUSTERS[cluster_name]
    jobs_url = f"{cluster_url}/jobs"

    try:
        response = requests.get(jobs_url, auth=AUTH, timeout=10)
        if response.status_code != 200:
            logger.error(f"❌ Failed to fetch jobs. Status: {response.status_code}")
            return

        jobs = response.json().get("jobs", [])
        job_id = None

        for job in jobs:
            if job["status"] == "RUNNING" and get_job_name(cluster_url, job["id"]) == job_name:
                job_id = job["id"]
                break

        if not job_id:
            logger.info(f"✅ No running job found with name '{job_name}'.")
            return

        # Termination URLs
        terminate_urls = [
            f"{cluster_url}/jobs/{job_id}/yarn-cancel",
            f"{cluster_url}/jobs/{job_id}/stop"
        ]

        termination_successful = False
        for url in terminate_urls:
            response = requests.get(url, auth=AUTH)
            if response.status_code in [200, 202]:
                termination_successful = True
                logger.info(f"🟡 Termination request accepted for Job ID {job_id}. Checking status...")
                break
            else:
                logger.error(f"❌ Termination failed for {job_id}. Response: {response.status_code}")

        # Confirm job termination
        if termination_successful:
            confirm_termination(cluster_url, [job_id])

    except requests.RequestException as e:
        logger.error(f"❌ Request failed: {e}")

def terminate_all_jobs(cluster_name):
    """Terminate all running jobs in a Flink cluster."""
    if cluster_name not in FLINK_CLUSTERS:
        logger.error(f"❌ Invalid cluster '{cluster_name}'. Check configuration.")
        return

    cluster_url = FLINK_CLUSTERS[cluster_name]
    jobs_url = f"{cluster_url}/jobs"

    try:
        response = requests.get(jobs_url, auth=AUTH, timeout=10)
        if response.status_code != 200:
            logger.error(f"❌ Failed to fetch jobs. Status: {response.status_code}")
            return

        jobs = response.json().get("jobs", [])
        running_jobs = [job["id"] for job in jobs if job["status"] == "RUNNING"]

        if not running_jobs:
            logger.info(f"✅ No running jobs found in cluster '{cluster_name}'.")
            return

        logger.info(f"🔄 Terminating all {len(running_jobs)} jobs...")

        for job_id in running_jobs:
            terminate_urls = [
                f"{cluster_url}/jobs/{job_id}/yarn-cancel",
                f"{cluster_url}/jobs/{job_id}/stop"
            ]

            for url in terminate_urls:
                response = requests.get(url, auth=AUTH)
                if response.status_code in [200, 202]:
                    logger.info(f"🟡 Termination request accepted for Job ID {job_id}.")
                    break
                else:
                    logger.error(f"❌ Termination failed for {job_id}. Response: {response.status_code}")

        # Confirm all jobs are terminated
        confirm_termination(cluster_url, running_jobs)

    except requests.RequestException as e:
        logger.error(f"❌ Request failed: {e}")

def confirm_termination(cluster_url, job_ids):
    """Repeatedly check job status to confirm termination."""
    logger.info(f"⏳ Waiting for jobs to stop...")

    for _ in range(6):  # Check status every 5 seconds for up to 30 seconds
        time.sleep(5)
        response = requests.get(f"{cluster_url}/jobs", auth=AUTH, timeout=10)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            still_running = [job for job in jobs if job["status"] == "RUNNING" and job["id"] in job_ids]

            if not still_running:
                logger.info(f"✅ All requested jobs are successfully terminated.")
                return
            else:
                logger.warning(f"⚠️ {len(still_running)} job(s) still running, retrying...")

    logger.error(f"❌ Some jobs are still running after multiple checks.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        logger.error("Usage:")
        logger.error("  python flink_terminate.py <cluster_name> <job_name>  # Terminate a specific job")
        logger.error("  python flink_terminate.py <cluster_name> --terminate-all  # Terminate all jobs in the cluster")
        sys.exit(1)

    cluster_name = sys.argv[1]
    job_name = sys.argv[2]

    if job_name == "--terminate-all":
        terminate_all_jobs(cluster_name)
    else:
        terminate_flink_job(cluster_name, job_name)
