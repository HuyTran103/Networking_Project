#!/usr/bin/env python3
"""
Twingate Resource Automation Script
Automatically discovers connectors in a remote network and registers
their IPs as accessible resources via the Twingate GraphQL API.
"""
 
import os
import sys
import argparse
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
 
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)
 
QUERY_REMOTE_NETWORKS = gql("""
query GetRemoteNetworkDetails {
  remoteNetworks(after: null, first: 10) {
    edges {
      node {
        id
        name
        connectors {
          edges {
            node {
              id
              name
              publicIP
              privateIPs
              remoteNetwork { id name }
            }
          }
        }
      }
    }
  }
}
""")
 
MUTATION_CREATE_RESOURCE = gql("""
mutation CreateResource($name: String!, $address: String!, $remoteNetworkId: ID!) {
  resourceCreate(name: $name, address: $address, remoteNetworkId: $remoteNetworkId) {
    ok
    error
    entity {
      id
      name
      address { type value }
    }
  }
}
""")
 
def load_env_file(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
 
def get_credentials():
    load_env_file()
    required = {
        "TWINGATE_API_URL": "https://<subdomain>.twingate.com/api/graphql/",
        "TWINGATE_API_KEY": None,
        "TWINGATE_NETWORK_NAME": None,
    }
    values = {}
    missing = []
    for key, example in required.items():
        val = os.environ.get(key)
        if not val:
            missing.append(f"  {key}" + (f"  (e.g. {example})" if example else ""))
        else:
            values[key] = val
    if missing:
        log.error("Missing required environment variables:\n" + "\n".join(missing))
        sys.exit(1)
    return values["TWINGATE_API_URL"], values["TWINGATE_API_KEY"], values["TWINGATE_NETWORK_NAME"]
 
def setup_client(api_url, api_key):
    transport = RequestsHTTPTransport(
        url=api_url,
        headers={"X-API-KEY": api_key},
        use_json=True,
        verify=True,
        retries=3,
    )
    return Client(transport=transport, fetch_schema_from_transport=True)
 
def get_target_network(client, network_name):
    response = client.execute(QUERY_REMOTE_NETWORKS)
    for edge in response["remoteNetworks"]["edges"]:
        node = edge["node"]
        if node["name"] == network_name:
            return node
    return None
 
def create_resource(client, name, address_value, remote_network_id):
    params = {"name": name, "address": address_value, "remoteNetworkId": remote_network_id}
    response = client.execute(MUTATION_CREATE_RESOURCE, variable_values=params)
    result = response["resourceCreate"]
    if not result["ok"]:
        raise RuntimeError(f"API rejected resource creation: {result['error']}")
    return result["entity"]
 
def automate_resource_creation(client, target_network, dry_run=False):
    network_id = target_network["id"]
    connectors = target_network["connectors"]["edges"]
    if not connectors:
        log.warning("No connectors found in this network.")
        return
    created = 0
    skipped = 0
    for conn_edge in connectors:
        connector = conn_edge["node"]
        conn_name = connector.get("name", "unknown")
        public_ip = connector.get("publicIP")
        private_ips = connector.get("privateIPs", [])
        log.info(f"Connector: {conn_name}")
        all_ips = []
        if public_ip:
            all_ips.append(("public", public_ip))
        for ip in private_ips:
            all_ips.append(("private", ip))
        if not all_ips:
            log.warning(f"  No IPs found for connector '{conn_name}', skipping.")
            skipped += 1
            continue
        for ip_type, ip in all_ips:
            label = ip.replace(".", "-")
            resource_name = f"{conn_name}-{ip_type}-{label}"
            if dry_run:
                log.info(f"  [DRY RUN] Would create: {resource_name} ({ip})")
                continue
            try:
                resource = create_resource(client, resource_name, ip, network_id)
                log.info(f"  Created: {resource['name']} | ID: {resource['id']}")
                created += 1
            except RuntimeError as e:
                log.error(f"  Failed for {ip}: {e}")
                skipped += 1
    if not dry_run:
        log.info(f"Done. {created} resource(s) created, {skipped} skipped.")
 
def parse_args():
    parser = argparse.ArgumentParser(description="Twingate Resource Automation")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()
 
def main():
    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    load_env_file(args.env_file)
    api_url, api_key, network_name = get_credentials()
    log.info(f"Connecting to Twingate API: {api_url}")
    log.info(f"Target network: {network_name}")
    client = setup_client(api_url, api_key)
    log.info("Searching for target network...")
    target_network = get_target_network(client, network_name)
    if not target_network:
        log.error(f"Network '{network_name}' not found.")
        sys.exit(1)
    log.info(f"Found network: {target_network['name']} (ID: {target_network['id']})")
    if args.dry_run:
        log.info("--- DRY RUN MODE: no changes will be made ---")
    automate_resource_creation(client, target_network, dry_run=args.dry_run)
 
if __name__ == "__main__":
    main()
