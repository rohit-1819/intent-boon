"""
discovery.py — Network state discovery.

When ONOS_ENABLED=true:  pulls live topology + telemetry from ONOS REST API
When ONOS_ENABLED=false: falls back to static CSV files (dev/offline mode)
"""

import os
import json
import csv

ONOS_ENABLED = os.environ.get("ONOS_ENABLED", "false").lower() == "true"

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

TOPOLOGY_FILE = os.path.join(PROJECT_ROOT, 'data', 'topology_metadata.json')
TELEMETRY_FILE = os.path.join(PROJECT_ROOT, 'data', 'raw_telemetry.csv')


def get_current_network_state() -> dict | None:
    """
    Returns network state dict:
    {
        "source":   "onos" | "csv",
        "topology": { "nodes": [...], "links": [...] },
        "telemetry": { "<node_id>": { metric: value, ... } }
    }
    """
    if ONOS_ENABLED:
        print("   [Discovery] ONOS_ENABLED=true — fetching live state...")
        state = _get_state_from_onos()
        if state:
            state["source"] = "onos"
            return state
        print("   [Discovery] ONOS fetch failed — falling back to CSV")

    print("   [Discovery] Using static CSV files (dev mode)")
    state = _get_state_from_csv()
    if state:
        state["source"] = "csv"
    return state


# ── ONOS live path ────────────────────────────────────────────────────────────

def _get_state_from_onos() -> dict | None:
    """
    Pulls topology from ONOS and telemetry from ONOS port stats.
    Two calls are made 5 seconds apart to get a real bandwidth delta.
    """
    try:
        import onos_client
        import time

        # Step 1: get topology
        topology = onos_client.get_topology()
        if not topology:
            print("   [Discovery] Could not get topology from ONOS")
            return None

        node_ids = [n["id"] for n in topology["nodes"]]

        # Step 2: first snapshot (establishes baseline, returns 0 Mbps)
        onos_client.get_live_telemetry(node_ids, topology["nodes"])

        # Step 3: wait then take real delta snapshot
        print("   [Discovery] Waiting 5s for bandwidth delta...")
        time.sleep(5)
        telemetry = onos_client.get_live_telemetry(node_ids, topology["nodes"])

        if not telemetry:
            print("   [Discovery] Telemetry came back empty")
            return None

        return {"topology": topology, "telemetry": telemetry}

    except Exception as e:
        print(f"   [Discovery] ONOS error: {e}")
        return None


# ── CSV static path ───────────────────────────────────────────────────────────

def _get_state_from_csv() -> dict | None:
    """
    Original discovery logic — reads topology_metadata.json
    and the most recent row per node from raw_telemetry.csv.
    """
    network_state = {"topology": {}, "telemetry": {}}

    # Load topology
    try:
        with open(TOPOLOGY_FILE, 'r') as f:
            network_state["topology"] = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Topology file not found: {TOPOLOGY_FILE}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Topology JSON malformed: {e}")
        return None

    # Load telemetry — take LAST row per node_id (most recent)
    try:
        with open(TELEMETRY_FILE, 'r') as f:
            reader = csv.DictReader(f)
            rows_by_node = {}
            for row in reader:
                node_id = row.get('node_id')
                if node_id:
                    rows_by_node[node_id] = row   # last row wins

        for node_id, row in rows_by_node.items():
            def safe_float(key, default=0.0):
                try:
                    return float(row[key])
                except (KeyError, ValueError):
                    return default

            network_state["telemetry"][node_id] = {
                "bandwidth_used_mbps":     safe_float('bandwidth_used_mbps'),
                "packet_loss_percent":     safe_float('packet_loss_percent'),
                "latency_ms":              safe_float('latency_ms'),
                "cpu_utilization_percent": safe_float('cpu_utilization_percent'),
                "active_flows":            safe_float('active_flows'),
                "buffer_occupancy":        safe_float('buffer_occupancy'),
                "jitter_ms":               safe_float('jitter_ms'),
            }

    except FileNotFoundError:
        print(f"[ERROR] Telemetry file not found: {TELEMETRY_FILE}")
        return None

    # Warn about nodes with no telemetry
    topo_ids     = {n["id"] for n in network_state["topology"].get("nodes", [])}
    telemetry_ids = set(network_state["telemetry"].keys())
    missing = topo_ids - telemetry_ids
    if missing:
        print(f"[WARN] Nodes with no telemetry: {missing}")

    return network_state