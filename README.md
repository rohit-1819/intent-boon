# 🌐 IntentBoon
### Semantic-Causal AI Engine for Intent-Driven Multimedia Traffic Scheduling

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" />
  <img src="https://img.shields.io/badge/SDN-ONOS%202.7-orange" />
  <img src="https://img.shields.io/badge/Data%20Plane-P4%20%2F%20bmv2-green" />
  <img src="https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-purple?logo=google" />
  <img src="https://img.shields.io/badge/Causal%20AI-DoWhy%200.11-red" />
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" />
</p>

---

## 📌 What is IntentBoon?

IntentBoon is an end-to-end intelligent network management framework that lets you say:

> *"my video call keeps freezing"*

…and have the network **automatically fix it** — without any manual configuration.

It combines three AI capabilities in a single pipeline:

| Capability | What it does |
|---|---|
| **Semantic AI** (Gemini 2.5 Flash) | Understands informal natural language and converts it into a structured JSON network policy |
| **Causal AI** (DoWhy GCM) | Asks *"would deploying this intent cause an SLA breach?"* using counterfactual P95 analysis — not just averages |
| **SDN Enforcement** (ONOS + P4Runtime) | Installs the resolution as a P4 match-action table entry on bmv2 switches via P4Runtime gRPC |

### Key Results
- ✅ **0.999 precision ratio** — recovers exactly the bandwidth needed, zero over-throttling
- ✅ **100% root-cause accuracy** — correctly distinguishes self-congestion from upstream switch flooding
- ✅ **Sub-30 second** full pipeline: parse → infer → resolve → enforce
- ✅ **Every decision is explainable** — causal chain + P50/P95 values + confidence score in every API response

---

## 🏗️ System Architecture

```
User (natural language)
        │
        ▼
┌─────────────────────────┐
│   Flask REST API        │  POST /translate
│   app.py                │
└────────────┬────────────┘
             │ intent JSON
             ▼
┌─────────────────────────┐
│   Semantic Engine       │  Gemini 2.5 Flash
│   semantic_engine.py    │  NL → JSON policy
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Orchestrator          │  Coordinates all modules
│   orchestrator.py       │  deploy / resolve / block
└──┬──────────┬───────────┘
   │          │
   ▼          ▼
┌──────┐  ┌──────────────────────────┐
│Disc- │  │  Inference Engine        │  DoWhy GCM
│overy │  │  inference.py            │  SCM + P95 Counterfactual
│.py   │  │                          │  Q1 (self) + Q2 (upstream)
└──┬───┘  └────────────┬─────────────┘
   │                   │
   │ network_state      │ counterfactual_details
   │                   ▼
   │      ┌────────────────────────┐
   │      │  Conflict Resolver     │  Causal Slope formula
   │      │  conflict_resolver.py  │  Minimum ΔBW recovery
   │      └────────────┬───────────┘
   │                   │
   └───────────────────┘
             │ enforcement actions
             ▼
┌─────────────────────────┐
│   ONOS Client           │  HTTP REST → ONOS
│   onos_client.py        │  ONOS → P4Runtime gRPC → bmv2
└─────────────────────────┘
```

---

## 📁 Repository Structure

```
IntentBoon/
│
├── README.md
├── requirements.txt
├── .env.example                  ← copy to .env and fill your keys
├── LICENSE
│
├── sdn/                          ← Everything SDN / P4 / ONOS side
│   │
│   ├── p4/
│   │   ├── main.p4               ← NGSDN P4 pipeline source
│   │   ├── build/
│   │   │   ├── ngsdn.json        ← Compiled bmv2 pipeline (p4c output)
│   │   │   └── p4info.txt        ← P4Info descriptor (used by ONOS)
│   │
│   ├── onos/
│   │   ├── pom.xml
│   │   ├── src/
|   |   |   ├── L2BridgingComponent.java
|   |   |   ├── MainComponent.java
|   |   |   └── QosRestServlet.java
│   │   └── README.txt
│   │
│   ├── mininet/
│   │   ├── topo.py         ← Mininet topology script (spine-leaf, 6 hosts, IPv6)
│   │   └── netcfg.json
│   │
│   └── docker-compose.yml        ← Starts ONOS 2.7 container with correct port bindings
│
├── ai/                           ← Everything AI / Python / Flask side
│   ├── sementic/
|   |   ├── app.py
|   |   ├── nexus_voice.py
|   |   ├── qos_mapping.py
|   |   ├── semantic_engine.py
|   |   └── templates/
|   |   |   └── index.html
|   |   
|   ├── Causal/
|   |   ├── models/
|   |   |   ├── casual_graph.py
|   |   |   └── structural_model.py
│   |   ├── src/
│   │   |   ├── orchestrator.py       ← Pipeline controller (deploy/resolve/block)
│   │   |   ├── inference.py          ← DoWhy GCM counterfactual engine (Q1 + Q2)
│   │   |   ├── conflict_resolver.py  ← Causal slope recovery + impact ranking
│   │   |   ├── discovery.py          ← ONOS topology + telemetry fetch
│   │   |   ├── onos_client.py        ← All ONOS REST API calls
|   |   |   └── __pycache__
│   │
│   ├── data/
│   │   ├── topology_metadata.json   ← Node/link definitions + service-to-host mapping
│   │   └── raw_telemetry.csv        ← Pre-recorded telemetry (used in STATIC mode)
│   │
│   ├── models/                   ← (optional) saved SCM model artifacts
│   │
│   ├── notebook/
│   │   └── exploration.ipynb     ← EDA, causal graph visualization, telemetry plots
│
├── frontend/                     ← (optional) simple web UI
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── docs/
    └── project_report.pdf        ← Full B.Tech project report
```

---

## ⚙️ Setup and Installation

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | All AI modules |
| Docker | 24.x | Run ONOS controller |
| Mininet | 2.3.0 | Virtual network |
| p4c | latest | Compile P4 program |
| bmv2 | latest | Software P4 switch |

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/IntentBoon.git
cd IntentBoon
```

### Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt includes:**
```
flask>=3.0
google-generativeai
dowhy>=0.11
networkx>=3.0
pandas>=1.4
numpy
requests
python-dotenv
```

### Step 3 — Set Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your_google_ai_studio_key
ONOS_ENABLED=false          # set true for live SDN mode
ONOS_HOST=localhost
ONOS_PORT=8181
ONOS_USER=onos
ONOS_PASSWORD=rocks
```

### Step 4 — Start ONOS Controller

```bash
cd sdn/
docker-compose up -d
```

Wait ~60 seconds for ONOS to boot, then activate required apps:

```bash
bash onos/activate_apps.sh
```

This activates: `org.onosproject.p4runtime`, `org.onosproject.drivers.bmv2`, `org.onosproject.pipelines.basic`, `org.onosproject.lldpprovider`, `org.onosproject.hostprovider`, `org.onosproject.rest`

### Step 5 — Start Mininet Topology

```bash
cd sdn/mininet/
sudo python3 ngsdn_topo.py
```

This starts 4 bmv2 switches + 6 hosts, pushes the compiled P4 pipeline to each switch via ONOS P4Runtime, and connects all switches to ONOS.

### Step 6 — Push ONOS Network Config

```bash
curl -u onos:rocks -X POST \
  -H "Content-Type: application/json" \
  -d @sdn/onos/netcfg.json \
  http://localhost:8181/onos/v1/network/configuration
```

### Step 7 — Start IntentBoon Flask Server

```bash
cd ai/
python3 src/app.py
```

The API is now live at `http://localhost:5000`

---

## 🚀 Usage

### Send a Natural Language Intent

```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "my video call keeps freezing, fix it"}'
```

### Example Response

```json
{
  "status": "deployed_after_resolution",
  "is_safe": true,
  "message": "Conflict resolved. spine1 throttled from 115.9 → 103.6 Mbps.",
  "counterfactual_details": {
    "latency_ms": {
      "p50": 40.28,
      "p95": 40.28,
      "sla_limit": 10.0,
      "root_cause": "both",
      "breach_predicted": true
    },
    "packet_loss_percent": {
      "p50": 0.06,
      "p95": 0.06,
      "sla_limit": 0.1,
      "root_cause": "none",
      "breach_predicted": false
    }
  },
  "onos_actuation": {
    "skipped": false,
    "throttle_rules_pushed": 1,
    "priority_rules_pushed": 1,
    "flow_ids": ["0x1a2b3c", "0x4d5e6f"]
  }
}
```

### Test Intents

| Say this... | System does... |
|---|---|
| `"my game is lagging badly"` | Protects gaming (h1a), DSCP EF priority |
| `"video call keeps freezing"` | Identifies VoIP SLA breach, throttles spine1 |
| `"i need smooth streaming"` | Guarantees video_stream (h1b) bandwidth |
| `"everything is slow"` | Scans all hosts, resolves worst breach first |

---

## 🧪 Running Tests

```bash
cd ai/
python3 -m pytest tests/ -v
```

---

## 📊 Results Summary

| Metric | Result |
|---|---|
| Causal Precision Ratio | 0.999 (zero over-throttling) |
| Root-cause accuracy | 100% correct in all congestion scenarios |
| Bandwidth recovered (vs greedy) | 12.3 Mbps (causal) vs 44.3 Mbps (greedy) |
| Full pipeline latency | < 30 seconds end-to-end |
| P4 flow rule installation | 100% ADDED state confirmed |
| SLA violations detected by P95 (missed by ATE) | ✅ All detected |

---

## 🔬 How the Causal Engine Works

```
Normal monitoring asks:  "What is the average latency?"
IntentBoon asks:         "What WOULD the P95 latency BE if I deploy this intent RIGHT NOW?"
```

**Two-Question Counterfactual Protocol:**
- **Q1** — Would the intent's own bandwidth demand overload the target host?
- **Q2** — Is an upstream switch already causing congestion that would breach the SLA regardless?

**Root cause classification:**
- `self` → only Q1 breaches → intent itself is the problem
- `upstream_switch` → only Q2 breaches → shared switch is the problem
- `both` → both breach → composite scenario, dual action needed
- `none` → neither breaches → safe to deploy

---

## 🗺️ Causal DAG

```
active_flows ──► bandwidth_used ──► buffer_occupancy ──► latency_ms
                                                      └──► jitter_ms
                                                      └──► packet_loss_%

cpu_utilization ─────────────────────────────────────► latency_ms
                                                      └──► jitter_ms

[INTER-NODE EDGE]
upstream_switch_bandwidth_used ──────────────────────► downstream_host_latency_ms
                                                      └──► downstream_host_jitter_ms
                                                      └──► downstream_host_packet_loss_%
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM / NLP | Google Gemini 2.5 Flash |
| Causal Inference | DoWhy 0.11 — InvertibleStructuralCausalModel |
| Web Framework | Flask 3.x |
| Graph Processing | NetworkX 3.x |
| Data Processing | pandas + numpy |
| SDN Controller | ONOS 2.7 LTS |
| Data Plane | P4 / bmv2 simple_switch_grpc |
| Control Protocol | P4Runtime gRPC |
| Network Emulation | Mininet + NGSDN topology |
| Containerisation | Docker |

---

## 👥 Team

| Name | Roll No. |
|---|---|
| Arti Devi | 2208410100016 |
| Gyanendra Singh | 2208410100028 |
| Mukund Gupta | 2208410100036 |
| Rohit Sharma | 2208410100049 |

**Supervisor:** Dr. Anurag Sewak (Assistant Professor, CSED)  
**Institution:** Rajkiya Engineering College Sonbhadra  
**University:** Dr. A.P.J. Abdul Kalam Technical University, Lucknow  

---

## 🙏 Acknowledgements

- [ONOS Project](https://opennetworking.org/onos/) — Open Network Operating System
- [DoWhy](https://py-why.github.io/dowhy/) — Microsoft Research causal inference library
- [P4 Language Consortium](https://p4.org/) — P4Runtime specification
- [p4lang/behavioral-model](https://github.com/p4lang/behavioral-model) — bmv2 software switch
- [NGSDN Tutorial](https://github.com/opennetworkinglab/ngsdn-tutorial) — NGSDN topology and P4 pipeline

---

<p align="center">Made with ❤️ at REC Sonbhadra · B.Tech CSE 2022–2026</p>
