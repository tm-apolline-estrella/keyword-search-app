# Import third-party library modules
import requests

# Import local modules
from src.components.coach_ai.settings import (
    APIM_END_POINT,
    APIM_SUB_KEY,
    NUM_AVAIL_CHECK,
    OPENAI_API_DEPLOYMENT_NAME,
    OPENAI_API_VERSION,
)


# based on https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
def check_azure_openai_availablity(log):
    log.info("Checking Azure availability...")
    for _ in range(NUM_AVAIL_CHECK):
        headers = {
            "api-key": APIM_SUB_KEY,
            "Content-Type": "application/json",
        }
        params = {"api-version": OPENAI_API_VERSION}
        try:
            # change how to check availability, since APIM
            # doesn't redirect to openai endpoint in general
            response = requests.post(
                f"{APIM_END_POINT}/openai/deployments/{OPENAI_API_DEPLOYMENT_NAME}/chat/completions",
                headers=headers,
                params=params,
                json={
                    "model": OPENAI_API_DEPLOYMENT_NAME,
                    "messages": [{"role": "user", "content": "Ping"}],
                },
            )

            log.info(f"Availability response is status code {response.status_code}")
            if response.status_code == 200:
                log.debug(response.json())
                return True
            else:
                log.debug(response.json())
                return False
        except Exception as e:
            log.error(f"Azure check: {e}")
    return False
