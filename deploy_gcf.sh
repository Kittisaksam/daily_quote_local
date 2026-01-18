#!/bin/bash

# Deployment script for Google Cloud Functions - Daily Quote Bot
# This script deploys the bot to Google Cloud Platform

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GOOGLE_CLOUD_REGION:-asia-southeast1}"
FUNCTION_NAME="daily-quote-bot"
SCHEDULER_NAME_MORNING="daily-quote-morning"
SCHEDULER_NAME_EVENING="daily-quote-evening"

# Function URLs (will be set after deployment)
FUNCTION_URL=""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Daily Quote Bot - GCF Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
echo -e "${YELLOW}Checking authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${RED}Error: Not authenticated with gcloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Prompt for project ID if not set
if [ "$PROJECT_ID" == "your-project-id" ]; then
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read -p "> " PROJECT_ID
fi

# Set the project
echo -e "${YELLOW}Setting project to: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Check if necessary APIs are enabled
echo ""
echo -e "${YELLOW}Checking required APIs...${NC}"
REQUIRED_APIS=(
    "cloudfunctions.googleapis.com"
    "cloudscheduler.googleapis.com"
    "pubsub.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" | grep -q "$api"; then
        echo -e "${GREEN}✓ $api is enabled${NC}"
    else
        echo -e "${YELLOW}Enabling $api...${NC}"
        gcloud services enable "$api" --async
    fi
done

# Deploy the Cloud Function
echo ""
echo -e "${YELLOW}Deploying Cloud Function...${NC}"

# Set environment variables for the function
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
echo -e "${GREEN}✓ Function deployed successfully!${NC}"
echo -e "${GREEN}Function URL: $FUNCTION_URL${NC}"

# Create Cloud Scheduler jobs
echo ""
echo -e "${YELLOW}Setting up Cloud Scheduler jobs...${NC}"

# Prompt for schedule times
echo ""
echo "Enter morning quote schedule time (cron format):"
echo "Example: '0 8 * * *' = 8:00 AM every day"
read -p "> " MORNING_SCHEDULE

echo "Enter evening quote schedule time (cron format):"
echo "Example: '0 20 * * *' = 8:00 PM every day"
read -p "> " EVENING_SCHEDULE

# Create morning scheduler
echo ""
echo -e "${YELLOW}Creating morning scheduler...${NC}"
gcloud scheduler jobs create http "$SCHEDULER_NAME_MORNING" \
    --schedule="$MORNING_SCHEDULE" \
    --time-zone="Asia/Bangkok" \
    --location="$REGION" \
    --uri="$FUNCTION_URL?period=morning" \
    --http-method=GET \
    --oidc-service-account-email="$(gcloud auth list --filter=status:ACTIVE --format='value(account)')" || {
    echo -e "${YELLOW}Morning scheduler might already exist. Updating...${NC}"
    gcloud scheduler jobs update http "$SCHEDULER_NAME_MORNING" \
        --schedule="$MORNING_SCHEDULE" \
        --uri="$FUNCTION_URL?period=morning" \
        --time-zone="Asia/Bangkok"
}

# Create evening scheduler
echo ""
echo -e "${YELLOW}Creating evening scheduler...${NC}"
gcloud scheduler jobs create http "$SCHEDULER_NAME_EVENING" \
    --schedule="$EVENING_SCHEDULE" \
    --time-zone="Asia/Bangkok" \
    --location="$REGION" \
    --uri="$FUNCTION_URL?period=evening" \
    --http-method=GET \
    --oidc-service-account-email="$(gcloud auth list --filter=status:ACTIVE --format='value(account)')" || {
    echo -e "${YELLOW}Evening scheduler might already exist. Updating...${NC}"
    gcloud scheduler jobs update http "$SCHEDULER_NAME_EVENING" \
        --schedule="$EVENING_SCHEDULE" \
        --uri="$FUNCTION_URL?period=evening" \
        --time-zone="Asia/Bangkok"
}

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Function URL: ${GREEN}$FUNCTION_URL${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo ""
echo -e "Test the function:"
echo -e "  curl \"$FUNCTION_URL?period=both\""
echo ""
echo -e "View logs:"
echo -e "  gcloud functions logs read $FUNCTION_NAME --region=$REGION --limit=50"
echo ""
echo -e "View scheduler jobs:"
echo -e "  gcloud scheduler jobs list --location=$REGION"
