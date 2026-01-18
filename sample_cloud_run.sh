# Clone your public repo into the temporary cloud environment
git clone https://github.com/RutanshuDesai/<repo_name>.git

# Move into the folder
cd <repo_name>

## Create the artifact repository
gcloud artifacts repositories create <repo_name>     --repository-format=docker     --location=us-east1     --description="Docker repository for my OCR app"

## Build the image
gcloud builds submit --tag us-east1-docker.pkg.dev/<project_id>/<repo_name>/<app_name> .

## Deploy the container as a service
gcloud run deploy my-service \
  --image us-east1-docker.pkg.dev/<project_id>/<repo_name>/<app_name> \
  --region us-east1 \
  --allow-unauthenticated \
  --max-instances 1
