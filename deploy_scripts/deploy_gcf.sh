#!/bin/bash

# Deployment script for Google Cloud Functions - Daily Quote Bot
set -e  # Exit on error

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GOOGLE_CLOUD_REGION:-asia-southeast1}"
FUNCTION_NAME="daily-quote-bot"
SCHEDULER_NAME_MORNING="daily-quote-morning"
SCHEDULER_NAME_EVENING="daily-quote-evening"

# Output colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No Color


# Helper functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}$1...${NC}"
}

print_error() {
    echo -e "${RED}Error: $1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}


# Pre-flight checks
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed"
        echo "Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        print_error "Not authenticated with gcloud"
        echo "Please run: gcloud auth login"
        exit 1
    fi
}

check_or_enable_api() {
    local api=$1
    if gcloud services list --enabled --filter="name:$api" | grep -q "$api"; then
        echo -e "${GREEN}✓ $api is enabled${NC}"
    else
        echo -e "${YELLOW}Enabling $api...${NC}"
        gcloud services enable "$api" --async
    fi
}


# Scheduler job management
create_or_update_scheduler() {
    local name=$1
    local schedule=$2
    local period=$3

    echo -e "${YELLOW}Creating $period scheduler...${NC}"

    local service_account=$(gcloud auth list --filter=status:ACTIVE --format='value(account)')
    local uri="$FUNCTION_URL?period=$period"

    if gcloud scheduler jobs create http "$name" \
        --schedule="$schedule" \
        --time-zone="Asia/Bangkok" \
        --location="$REGION" \
        --uri="$uri" \
        --http-method=GET \
        --oidc-service-account-email="$service_account" 2>/dev/null; then
        print_success "$period scheduler created"
    else
        echo -e "${YELLOW}$period scheduler already exists. Updating...${NC}"
        gcloud scheduler jobs update http "$name" \
            --schedule="$schedule" \
            --uri="$uri" \
            --time-zone="Asia/Bangkok"
    fi
}


# Main deployment flow
print_header "Daily Quote Bot - GCF Deployment"

# Check prerequisites
check_gcloud
print_step "Checking authentication"
check_auth

# Set project
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -n "Enter your Google Cloud Project ID: "
    read -r PROJECT_ID
fi

print_step "Setting project to: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

# Check and enable required APIs
echo ""
print_step "Checking required APIs"
for api in "cloudfunctions.googleapis.com" "cloudscheduler.googleapis.com" "pubsub.googleapis.com"; do
    check_or_enable_api "$api"
done

# Deploy the Cloud Function
echo ""
print_step "Deploying Cloud Function"

gcloud functions deploy "$FUNCTION_NAME" \
    --runtime=python311 \
    --region="$REGION" \
    --source=. \
    --entry-point=send_daily_quote \
    --requirements-file=gcf_requirements.txt \
    --allow-unauthenticated \
    --set-env-vars=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN",TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID",ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    --memory=256MB \
    --timeout=60s \
    --max-instances=1

# Get the function URL
FUNCTION_URL=$(gcloud functions describe "$FUNCTION_NAME" \
    --region="$REGION" \
    --format="value(httpsTrigger.url)")

echo ""
print_success "Function deployed successfully!"
echo -e "Function URL: ${GREEN}$FUNCTION_URL${NC}"

# Setup Cloud Scheduler jobs
echo ""
print_step "Setting up Cloud Scheduler jobs"

echo ""
echo "Enter morning quote schedule time (cron format):"
echo "Example: '0 8 * * *' = 8:00 AM every day"
read -p "> " MORNING_SCHEDULE

echo ""
echo "Enter evening quote schedule time (cron format):"
echo "Example: '0 20 * * *' = 8:00 PM every day"
read -p "> " EVENING_SCHEDULE

echo ""
create_or_update_scheduler "$SCHEDULER_NAME_MORNING" "$MORNING_SCHEDULE" "morning"
create_or_update_scheduler "$SCHEDULER_NAME_EVENING" "$EVENING_SCHEDULE" "evening"

# Summary
echo ""
print_header "Deployment Complete!"
echo ""
echo -e "Function URL: ${GREEN}$FUNCTION_URL${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo ""
echo "Test the function:"
echo -e "  curl \"${GREEN}$FUNCTION_URL${NC}?period=both\""
echo ""
echo "View logs:"
echo -e "  gcloud functions logs read $FUNCTION_NAME --region=$REGION --limit=50"
echo ""
echo "View scheduler jobs:"
echo -e "  gcloud scheduler jobs list --location=$REGION"
echo ""
