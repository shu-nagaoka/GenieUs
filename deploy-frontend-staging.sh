#!/bin/bash
set -e

cd /Users/tnoce/dev/GenieUs/frontend

# Get backend URL
BACKEND_URL=$(gcloud run services describe genius-backend-staging \
  --region=asia-northeast1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"

# Deploy frontend
gcloud run deploy genius-frontend-staging \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 3000 \
  --cpu 1 \
  --memory 1Gi \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars "NODE_ENV=production" \
  --set-env-vars "NEXT_PUBLIC_API_BASE_URL=$BACKEND_URL" \
  --set-env-vars "NEXTAUTH_SECRET=wMZZquMg1ur7aLtT4QDBDqgVtZv6Nu8lZPZuiTyl74Q=" \
  --set-env-vars "GOOGLE_CLIENT_ID=280304291898-jvpopea09pfhv1nckpl697rd34krguf1.apps.googleusercontent.com" \
  --set-env-vars "GOOGLE_CLIENT_SECRET=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" \
  --timeout 600 \
  --quiet

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe genius-frontend-staging \
  --region=asia-northeast1 \
  --format='value(status.url)')

# Update NEXTAUTH_URL
echo "Updating NEXTAUTH_URL to: $FRONTEND_URL"
gcloud run services update genius-frontend-staging \
  --region=asia-northeast1 \
  --update-env-vars "NEXTAUTH_URL=$FRONTEND_URL" \
  --quiet

# Update backend CORS
echo "Updating backend CORS to: $FRONTEND_URL"
gcloud run services update genius-backend-staging \
  --region=asia-northeast1 \
  --update-env-vars "CORS_ORIGINS=$FRONTEND_URL" \
  --quiet

echo "Deployment complete!"
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"