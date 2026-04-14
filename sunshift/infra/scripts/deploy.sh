#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"

usage() {
    echo "Usage: $0 <environment> <command>"
    echo ""
    echo "Environments: dev, prod"
    echo "Commands: init, plan, apply, destroy, output"
    echo ""
    echo "Examples:"
    echo "  $0 dev init     # Initialize Terraform for dev"
    echo "  $0 dev plan     # Show planned changes"
    echo "  $0 dev apply    # Apply changes"
    echo "  $0 dev output   # Show outputs"
    exit 1
}

if [[ $# -lt 2 ]]; then
    usage
fi

ENVIRONMENT="$1"
COMMAND="$2"
ENV_DIR="${INFRA_DIR}/environments/${ENVIRONMENT}"

if [[ ! -d "$ENV_DIR" ]]; then
    echo "Error: Environment '$ENVIRONMENT' not found at $ENV_DIR"
    exit 1
fi

cd "$ENV_DIR"

case "$COMMAND" in
    init)
        echo "Initializing Terraform for ${ENVIRONMENT}..."
        terraform init
        ;;
    plan)
        echo "Planning changes for ${ENVIRONMENT}..."
        terraform plan -out=tfplan
        ;;
    apply)
        if [[ -f "tfplan" ]]; then
            echo "Applying saved plan for ${ENVIRONMENT}..."
            terraform apply tfplan
            rm -f tfplan
        else
            echo "Applying changes for ${ENVIRONMENT}..."
            terraform apply
        fi
        ;;
    destroy)
        echo "WARNING: This will destroy all resources in ${ENVIRONMENT}!"
        read -p "Type 'yes' to confirm: " confirm
        if [[ "$confirm" == "yes" ]]; then
            terraform destroy
        else
            echo "Aborted."
            exit 1
        fi
        ;;
    output)
        terraform output
        ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
