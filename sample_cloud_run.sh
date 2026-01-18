# Clone your public repo into the temporary cloud environment OR git pull if already cloned and in the directory
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


## configuring secret and allowing the access to cloud run  
# Give permission to the default compute service account
gcloud secrets add-iam-policy-binding APP_USERNAME \
    --member="serviceAccount:<project_number>-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding APP_PASSWORD \
    --member="serviceAccount:<project_number>-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"