# Putting in production by deploying to the Cloud
# Google Cloud Run is serverless, scales to zero, and fits bursty workloads.
# With free tier compute, it can be mostly free to run.

# 1) Create a GCP project
# - Create/select a project in the GCP Console and enable billing.
# - Cloud Shell is pre-configured with gcloud for quick setup.

# 2) Enable the required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com

# 3) Clone the repo in Cloud Shell
git clone https://github.com/RutanshuDesai/ocr_to_text_app.git
cd ocr_to_text_app

# 4) Containerize (Docker)
# Dockerfile:
# - Installs Tesseract + Gujarati language pack (tesseract-ocr-guj)
# - Installs Python deps from requirements.txt
# - Runs Streamlit on port 8080 and binds to 0.0.0.0

# 5) Create an Artifact Registry (Docker) repository
# This is where your built container images will live.

# Replace [REGION] with your preferred location (e.g., us-east1)
gcloud artifacts repositories create ocr-to-text-app \
    --repository-format=docker \
    --location=[REGION] \
    --description="Production OCR Images"

# 6) Build + push the container image with Cloud Build
# This builds the Dockerfile image and pushes to Artifact Registry.

# Replace the placeholders with your specific project details
gcloud builds submit --tag [REGION]-docker.pkg.dev/[PROJECT_ID]/ocr-to-text-app/ocr-image:v1 .

# 7) Store login credentials in Secret Manager
# The app reads APP_USERNAME and APP_PASSWORD from env vars.
# - Create two secrets in Secret Manager.
# - Grant Cloud Run runtime identity access to read them.

# Granting the default compute service account access to the secrets
# Replace [PROJECT_NUMBER] with your actual GCP project number
gcloud secrets add-iam-policy-binding APP_USERNAME \
    --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding APP_PASSWORD \
    --member="serviceAccount:[PROJECT_NUMBER]-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# 8) Deploy to Cloud Run
gcloud run deploy ocr-to-text-app-service \
  --image [REGION]-docker.pkg.dev/[PROJECT_ID]/ocr-to-text-app/ocr-image:v1 \
  --region [REGION] \
  --allow-unauthenticated \
  --max-instances 1 \
  --concurrency 5 \
  --cpu-boost

# Make sure secrets are exposed as env vars in Cloud Run settings.
# Cloud Run will output a URL. That’s your production app.

# Updating the App in Production (Easy Re-deploy)
# 1) Push your code changes to GitHub
git add .
git commit -m "Describe your update"
git push origin main

# 2) Pull latest changes and rebuild the image
cd ocr_to_text_app
git pull
gcloud builds submit --tag [REGION]-docker.pkg.dev/[PROJECT_ID]/ocr-to-text-app/ocr-image:v2 .

# 3) Re-deploy the latest image to Cloud Run
gcloud run deploy ocr-to-text-app-service \
  --image [REGION]-docker.pkg.dev/[PROJECT_ID]/ocr-to-text-app/ocr-image:v2 \
  --region [REGION]

# That's it! Your changes go live in less than five minutes.