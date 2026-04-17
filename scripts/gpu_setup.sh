#!/usr/bin/env bash
# ============================================================
# scripts/gpu_setup.sh — Arc Fleet GCP GPU Instance Setup
#
# Supports:
#   Local:   V100 SXM2 8x32GB (your own server, shipping soon)
#   Rental:  GCP n1-standard + NVIDIA GPU (V100/A100/T4/L4/P100)
#   Budget:  T4 ($0.35/hr) → A100 ($2.93/hr) → H100 ($10+/hr)
#
# Usage:
#   ./scripts/gpu_setup.sh --list-gpus         # Show available GPUs + prices
#   ./scripts/gpu_setup.sh --create t4         # Spin up T4 instance
#   ./scripts/gpu_setup.sh --create v100       # Spin up V100 instance
#   ./scripts/gpu_setup.sh --create a100       # Spin up A100 instance
#   ./scripts/gpu_setup.sh --stop INSTANCE     # Stop (keep disk)
#   ./scripts/gpu_setup.sh --delete INSTANCE   # Delete instance + disk
#   ./scripts/gpu_setup.sh --ssh INSTANCE      # SSH into instance
#   ./scripts/gpu_setup.sh --local-setup       # Setup local V100 server
#   ./scripts/gpu_setup.sh --budget 300        # Estimate what $300 buys
# ============================================================

set -euo pipefail

GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'
CYAN='\033[96m'; BOLD='\033[1m'; RESET='\033[0m'

ok()     { echo -e "  ${GREEN}✓${RESET} $1"; }
warn()   { echo -e "  ${YELLOW}⚠${RESET} $1"; }
err()    { echo -e "  ${RED}✗${RESET} $1"; }
info()   { echo -e "  ${CYAN}→${RESET} $1"; }
banner() { echo -e "\n${CYAN}══════════════════════════════════════════════════════════${RESET}"; echo -e "  ${BOLD}$1${RESET}"; echo -e "${CYAN}══════════════════════════════════════════════════════════${RESET}\n"; }

# ── Load .env ─────────────────────────────────────────────────────────────────
[[ -f .env ]] && { set -a; source .env; set +a; }

PROJECT_ID="${GCP_PROJECT_ID:-arc-fleet-campaign}"
REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"
SA_EMAIL="${GCP_SA_EMAIL:-}"

# ── GPU Catalog ───────────────────────────────────────────────────────────────
declare -A GPU_TYPES=(
    # Format: "machine_type|gpu_type|gpu_count|price_hr|vram_gb|use_case"
    [t4]="n1-standard-4|nvidia-tesla-t4|1|0.35|16|Dev/inference/fine-tune small models"
    [p4]="n1-standard-4|nvidia-tesla-p4|1|0.60|8|Inference, older models"
    [p100]="n1-standard-8|nvidia-tesla-p100|1|1.46|16|Training mid-size, good price/perf"
    [v100]="n1-standard-8|nvidia-tesla-v100|1|2.48|16|Training, fast"
    [v100x4]="n1-standard-32|nvidia-tesla-v100|4|9.92|64|Multi-GPU training"
    [a100-40]="a2-highgpu-1g|nvidia-tesla-a100|1|2.93|40|High-perf training"
    [a100-80]="a2-ultragpu-1g|nvidia-a100-80gb|1|5.15|80|Large model fine-tune"
    [l4]="g2-standard-4|nvidia-l4|1|0.70|24|Modern inference, efficient"
    [l40s]="g2-standard-48|nvidia-l40s|4|8.20|192|High-end inference, local replacement"
    [h100]="a3-highgpu-8g|nvidia-h100-80gb|8|32.77|640|Top training, expensive"
)

list_gpus() {
    banner "GCP GPU Catalog — Arc Fleet"
    printf "  %-12s %-20s %-5s %-8s %-8s %s\n" "KEY" "GPU TYPE" "COUNT" "PRICE/HR" "VRAM" "USE CASE"
    echo "  $(printf '%.0s─' {1..80})"
    for key in t4 p4 p100 v100 v100x4 a100-40 a100-80 l4 l40s h100; do
        IFS='|' read -r mtype gpu cnt price vram use <<< "${GPU_TYPES[$key]}"
        printf "  %-12s %-20s %-5s \$%-7s %-8s %s\n" "$key" "$gpu" "$cnt" "$price" "${vram}GB" "$use"
    done
    echo ""
    echo -e "  ${CYAN}Your local server (shipping soon):${RESET}"
    echo -e "  V100 SXM2 ×8  — 32GB each = 256GB total VRAM"
    echo -e "  Equivalent GCP cost: ~\$19.84/hr  (\$475/day  \$14,256/mo)"
    echo -e "  → Run locally for sustained training, GCP for burst/experiments"
    echo ""
    echo -e "  ${CYAN}Budget estimates:${RESET}"
    echo "  \$300 GCP credit → T4: ~857 hrs | V100: ~120 hrs | A100-40: ~102 hrs"
}

budget_estimate() {
    local budget="${1:-300}"
    banner "Budget Estimate: \$$budget"
    for key in t4 l4 p100 v100 a100-40 a100-80; do
        IFS='|' read -r mtype gpu cnt price vram use <<< "${GPU_TYPES[$key]}"
        hours=$(echo "scale=1; $budget / $price" | bc)
        days=$(echo "scale=1; $hours / 24" | bc)
        printf "  %-12s \$%s/hr → %s hrs  (%s days)  [%sGB VRAM]\n" \
               "$key" "$price" "$hours" "$days" "$vram"
    done
    echo ""
    warn "GCP free tier does NOT include GPU instances."
    info "Activate billing + request GPU quota first (see below)."
}

# ── Create instance ───────────────────────────────────────────────────────────
create_instance() {
    local gpu_key="${1:-t4}"
    local name="${2:-arc-fleet-gpu-$(date +%Y%m%d)}"

    IFS='|' read -r mtype gputype cnt price vram use <<< "${GPU_TYPES[$gpu_key]:-}"
    if [[ -z "$mtype" ]]; then
        err "Unknown GPU type: $gpu_key. Run --list-gpus to see options."
        exit 1
    fi

    banner "Creating GCP GPU Instance: $name"
    info "GPU:      $gputype × $cnt  ($vram GB VRAM)"
    info "Machine:  $mtype"
    info "Cost:     ~\$$price/hr"
    info "Zone:     $ZONE"
    info "Project:  $PROJECT_ID"

    echo ""
    read -r -p "  Confirm creation? [y/N] " confirm
    [[ "${confirm,,}" != "y" ]] && { info "Cancelled."; exit 0; }

    # Request GPU quota first if needed
    info "Checking GPU quota ..."
    gcloud compute instances create "$name" \
        --project="$PROJECT_ID" \
        --zone="$ZONE" \
        --machine-type="$mtype" \
        --accelerator="type=$gputype,count=$cnt" \
        --maintenance-policy=TERMINATE \
        --image-family=pytorch-latest-gpu \
        --image-project=deeplearning-platform-release \
        --boot-disk-size=100GB \
        --boot-disk-type=pd-ssd \
        --scopes=https://www.googleapis.com/auth/cloud-platform \
        ${SA_EMAIL:+--service-account="$SA_EMAIL"} \
        --metadata="install-nvidia-driver=True" \
        --tags=arc-fleet,gpu-instance

    ok "Instance created: $name"
    info "SSH: gcloud compute ssh $name --zone=$ZONE --project=$PROJECT_ID"
    info "Stop: ./scripts/gpu_setup.sh --stop $name"
    info "Delete: ./scripts/gpu_setup.sh --delete $name"

    # Save instance name to .env
    echo "LAST_GPU_INSTANCE=$name" >> .env
}

# ── Stop / Delete ─────────────────────────────────────────────────────────────
stop_instance() {
    local name="${1}"
    banner "Stopping: $name"
    gcloud compute instances stop "$name" --zone="$ZONE" --project="$PROJECT_ID"
    ok "Stopped. Disk preserved. Resume: gcloud compute instances start $name --zone=$ZONE"
}

delete_instance() {
    local name="${1}"
    banner "DELETING: $name"
    warn "This will DELETE the instance AND its disk permanently."
    read -r -p "  Type instance name to confirm: " confirm
    [[ "$confirm" != "$name" ]] && { info "Cancelled."; exit 0; }
    gcloud compute instances delete "$name" --zone="$ZONE" --project="$PROJECT_ID" --quiet
    ok "Deleted: $name"
}

ssh_instance() {
    local name="${1:-${LAST_GPU_INSTANCE:-}}"
    [[ -z "$name" ]] && { err "No instance name provided."; exit 1; }
    gcloud compute ssh "$name" --zone="$ZONE" --project="$PROJECT_ID"
}

# ── Local V100 SXM2 Server Setup ─────────────────────────────────────────────
local_setup() {
    banner "Local V100 SXM2 Server Setup (8× 32GB = 256GB VRAM)"

    cat <<'SETUP'
  ┌─────────────────────────────────────────────────────────────┐
  │ V100 SXM2 8× 32GB — Local Server Setup                      │
  │ (Run these commands on the server when it arrives)           │
  └─────────────────────────────────────────────────────────────┘

  1. NVIDIA DRIVERS (Ubuntu 22.04)
     sudo apt update && sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit
     nvidia-smi   # verify all 8 GPUs visible

  2. DOCKER + NVIDIA CONTAINER TOOLKIT
     curl https://get.docker.com | sh
     distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
     curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
     curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list \
         | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
     sudo apt update && sudo apt install -y nvidia-container-toolkit
     sudo systemctl restart docker

  3. VERIFY ALL 8 GPUs
     docker run --gpus all nvidia/cuda:12.0-base nvidia-smi
     # Should show: 8× V100 SXM2 32GB

  4. PYTHON + ML STACK
     python3 -m pip install torch torchvision torchaudio \
         --index-url https://download.pytorch.org/whl/cu121
     python3 -c "import torch; print(torch.cuda.device_count(), 'GPUs')"

  5. PYTORCH MULTI-GPU TEST
     python3 -c "
     import torch
     print(f'GPUs: {torch.cuda.device_count()}')
     for i in range(torch.cuda.device_count()):
         print(f'  GPU {i}: {torch.cuda.get_device_name(i)}  VRAM: {torch.cuda.get_device_properties(i).total_memory//1e9:.0f}GB')
     "

  6. CONNECT TO GCP (optional — for syncing models/data)
     gcloud auth application-default login
     gsutil cp gs://$GCP_BUCKET/models/. ./models/

  7. ARC FLEET SETUP ON LOCAL SERVER
     git clone https://github.com/YOUR_REPO/arc-fleet-campaign .
     cp .env.example .env && nano .env
     python setup_wizard.py --section gpu

  8. VERTEX AI WORKBENCH CONNECTION (optional)
     # Register local as a custom runtime in Vertex AI Workbench
     # https://cloud.google.com/vertex-ai/docs/workbench/user-managed/custom-env

SETUP

    ok "Instructions printed. Run on the V100 server when it arrives."
}

# ── GCP Quota + Billing setup ─────────────────────────────────────────────────
gcp_quota_setup() {
    banner "GCP GPU Quota Setup"
    cat <<'QUOTA'
  ┌─────────────────────────────────────────────────────────────┐
  │ GCP GPU Quota — Must request before creating GPU instances  │
  └─────────────────────────────────────────────────────────────┘

  1. Enable Billing (if not done):
     https://console.cloud.google.com/billing

  2. Enable Compute Engine API:
     gcloud services enable compute.googleapis.com

  3. Request GPU quota:
     https://console.cloud.google.com/iam-admin/quotas
     Search: "NVIDIA T4 Virtual Workstations" or "NVIDIA V100"
     Request: at least 1 (T4) or 8 (V100/A100 for multi-GPU)
     Note: Approval takes 1-2 business days.

  4. Free Tier + Credits:
     - New accounts get $300 credit (90 days)
     - T4 at $0.35/hr = ~857 hours of GPU compute
     - Apply for ML startup credits:
       https://cloud.google.com/programs/startups

  5. Set billing alert to avoid overruns:
     gcloud billing budgets create \
         --billing-account=BILLING_ACCOUNT_ID \
         --display-name="Arc Fleet Budget" \
         --budget-amount=300USD \
         --threshold-rule=percent=50 \
         --threshold-rule=percent=90 \
         --threshold-rule=percent=100

QUOTA
}

# ── Top 10 GPU Projects (printed) ─────────────────────────────────────────────
top10_projects() {
    banner "Top 10 Arc Fleet GPU Projects"
    cat <<'PROJ'
  GPU: T4 ($0.35/hr), V100 local (free), A100 ($2.93/hr), H100 ($32/hr)

  ┌────┬──────────────────────────────────────┬────────┬─────────────────────┐
  │ #  │ Project                              │ GPU    │ Est. Cost           │
  ├────┼──────────────────────────────────────┼────────┼─────────────────────┤
  │  1 │ Fine-tune Gemma 2B → vehicle QA bot │ T4×1   │ $5-15 (T4 per run)  │
  │  2 │ Whisper STT (call transcription)     │ T4×1   │ $2-5/day inference  │
  │  3 │ LLM Sluice: lead qualifier fine-tune│ V100×1 │ Free (local)        │
  │  4 │ Embedding: vehicle listing search    │ T4×1   │ $1-3 one-time       │
  │  5 │ Multi-agent sim: robot-vs-robot test │ T4×1   │ $3-8 dev runs       │
  │  6 │ LoRA fine-tune: sales voice persona  │ V100×4 │ Free (local 8×)     │
  │  7 │ RAG pipeline: CRM + BigQuery         │ T4×1   │ $5-10 dev           │
  │  8 │ Playwright vision: form-fill VLM     │ L4×1   │ $15-30 dev          │
  │  9 │ Gemini custom fine-tune (Vertex AI)  │ A100   │ $50-200 (managed)   │
  │ 10 │ Multi-GPU: llama.cpp 70B local test  │ V100×8 │ Free (local server) │
  └────┴──────────────────────────────────────┴────────┴─────────────────────┘

  Priority order:
    Phase 1 (now, $0-20):   #1 #2 #3 #5  — T4 GCP or local V100
    Phase 2 (local server): #6 #7 #10    — 8×V100 SXM2
    Phase 3 ($100-300):     #4 #8 #9     — A100/L4 GCP

  Commands:
    ./scripts/gpu_setup.sh --create t4       # Start Phase 1
    ./scripts/gpu_setup.sh --local-setup     # Prepare local server
    ./scripts/gpu_setup.sh --budget 300      # Plan $300 credit usage

PROJ
}

# ── Main ──────────────────────────────────────────────────────────────────────
case "${1:-}" in
    --list-gpus|--list) list_gpus ;;
    --budget)           budget_estimate "${2:-300}" ;;
    --create)           create_instance "${2:-t4}" "${3:-}" ;;
    --stop)             stop_instance "${2}" ;;
    --delete)           delete_instance "${2}" ;;
    --ssh)              ssh_instance "${2:-}" ;;
    --local-setup)      local_setup ;;
    --quota)            gcp_quota_setup ;;
    --top10)            top10_projects ;;
    --all-info)
        list_gpus
        budget_estimate 300
        top10_projects
        ;;
    *)
        banner "Arc Fleet GPU Setup"
        echo "  Usage: $0 <command>"
        echo ""
        echo "  --list-gpus          Show GPU catalog + prices"
        echo "  --budget [N]         Estimate what \$N buys"
        echo "  --create [type]      Create GCP GPU instance (t4|v100|a100-40|...)"
        echo "  --stop   [name]      Stop instance (keep disk)"
        echo "  --delete [name]      Delete instance + disk"
        echo "  --ssh    [name]      SSH into instance"
        echo "  --local-setup        Setup your local V100 SXM2 server"
        echo "  --quota              GCP GPU quota request instructions"
        echo "  --top10              Show top 10 GPU project ideas"
        echo "  --all-info           Show everything"
        ;;
esac
