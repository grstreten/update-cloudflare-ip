import requests
import os
import time
import json

# Cloudflare API configuration
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
APPLICATION_IDS = json.loads(os.getenv("APPLICATION_IDS", "[]"))
POLICY_NAME = os.getenv("POLICY_NAME", "Bypass Policy for Current Public IP")

if len(APPLICATION_IDS) < 1:
    print('** ERROR: At least one Application ID must be specified using APPLICATION_IDS in a JSON list format')
    exit(0)

print("** Script started")

# Helper function to get the current public IP address
def get_public_ip():
    try:
        response = requests.get("https://icanhazip.com")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None


# Helper function to fetch existing policies for an application
def get_existing_policy_id(application_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/access/apps/{application_id}/policies"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        policies = response.json().get("result", [])
        for policy in policies:
            if policy.get("name") == POLICY_NAME:
                return policy.get("id")
        return None
    except requests.RequestException as e:
        print(f"Error fetching policies for application {application_id}: {e}")
        return None


# Helper function to update an existing Cloudflare Access policy
def update_cloudflare_policy(application_id, policy_id, ip_address):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/access/apps/{application_id}/policies/{policy_id}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    policy_payload = {
        "precedence": 1,
        "decision": "bypass",
        "include": [{"ip": {"ip": ip_address}}],
        "name": POLICY_NAME,
    }

    try:
        response = requests.put(url, headers=headers, json=policy_payload)
        response.raise_for_status()
        print(
            f"Successfully updated policy for application {application_id} with IP: {ip_address}"
        )
    except requests.RequestException as e:
        print(f"Error updating policy for application {application_id}: {e}")


def get_next_available_precedence(application_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/access/apps/{application_id}/policies"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        policies = response.json().get("result", [])
        used_precedences = {policy.get("precedence") for policy in policies}
        # Find the lowest available precedence starting from 1
        precedence = 1
        while precedence in used_precedences:
            precedence += 1
        return precedence
    except requests.RequestException as e:
        print(f"Error fetching policies for application {application_id}: {e}")
        return 1  # Default to 1 if there's an error


# Helper function to create a new Cloudflare Access policy
def create_cloudflare_policy(application_id, ip_address):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/access/apps/{application_id}/policies"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    precedence = get_next_available_precedence(application_id)

    policy_payload = {
        "precedence": precedence,
        "decision": "bypass",
        "include": [{"ip": {"ip": ip_address}}],
        "require": [],
        "exclude": [],
        "name": POLICY_NAME,
    }

    try:
        response = requests.post(url, headers=headers, json=policy_payload)
        response.raise_for_status()
        print(
            f"Successfully created new policy for application {application_id} with IP: {ip_address} and precedence: {precedence}"
        )
    except requests.RequestException as e:
        print(f"Error creating policy for application {application_id}: {e}")
        print(f"Response content: {response.content}")


# Main function to update or create policies for all applications
def main():
    while True:
        public_ip = get_public_ip()
        if public_ip:
            for application_id in APPLICATION_IDS:
                policy_id = get_existing_policy_id(application_id)
                if policy_id:
                    update_cloudflare_policy(application_id, policy_id, public_ip)
                else:
                    create_cloudflare_policy(application_id, public_ip)
        else:
            print("Failed to fetch public IP. Skipping update.")

        print('Sleepy time for 10 minutes')
        # Wait 10 minutes before checking again
        time.sleep(600)


if __name__ == "__main__":
    main()
