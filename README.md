# Regional Language Text Extractor (OCR)

A web application for extracting text from scanned PDFs, TIF, and image files using Tesseract OCR. Built with Streamlit, it is easy to deploy on any cloud platform or self-hosted environment. The current deployment uses Google Cloud.

## The Problem

Many legal and administrative documents are written in regional languages and need to be translated into English for use in judicial courts or official purposes. These documents often exist as hard copies, PDFs, or images. Hard copies, in particular, can be easily digitized by scanning them into TIF image files, which can then be uploaded and processed by the application. Extracting text from such documents manually is tedious and error-prone. Existing OCR solutions frequently lack robust support for regional languages or require expensive subscriptions.

## The Solution

This application provides a simple, self-hosted OCR solution that:

- Supports multiple file formats (PDF, TIF, TIFF, PNG, JPG, JPEG), including scanned hard copies uploaded as TIF images
- Works with any language supported by Tesseract (100+ languages)
- Runs entirely in your own infrastructure (no data sent to third parties)
- Offers a clean web interface for non-technical users
- Deploys easily to Google Cloud Run for scalable, low-cost hosting

## Features

- **Multi-format support**: Process scanned PDFs, TIF/TIFF, PNG, and JPEG files
- **Multi-language OCR**: Default configured for Gujarati, but supports all Tesseract languages
- **Simple authentication**: Basic username/password protection
- **One-click download**: Download extracted text as a `.txt` file
- **Cloud-ready**: Containerized with Docker for easy deployment

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│   PyMuPDF       │────▶│   Tesseract     │
│   Web UI        │     │  (PDF → Image,  │     │   OCR Engine    │
└─────────────────┘     │  skip if image) │     └─────────────────┘
        ▲               └─────────────────┘             │
        │                                               │
        │                                               ▼
┌─────────────────┐                            ┌─────────────────┐
│  File Upload    │                            │  Extracted Text │
│  (PDF/TIF/IMG)  │                            │  (.txt download)│
└─────────────────┘                            └─────────────────┘
```

**Components:**
- **Streamlit**: Web framework providing the user interface
- **PyMuPDF (fitz)**: Converts PDF pages to images for OCR processing if needed
- **Pillow**: Image processing library
- **Tesseract OCR**: Open-source OCR engine for text extraction

## Quick Start

### Prerequisites

- Python 3.11+
- Tesseract OCR installed on your system

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/RutanshuDesai/pdf-translation-business.git
   cd pdf-translation-business
   ```

2. **Install Tesseract OCR**

   macOS:
   ```bash
   brew install tesseract tesseract-lang
   ```

   Ubuntu/Debian:
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-guj
   ```

   Windows:
   Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

3. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env-example .env
   ```
   
   Edit `.env` and set your credentials:
   ```
   APP_USERNAME=your_username
   APP_PASSWORD=your_secure_password
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The app will be available at `http://localhost:8501`

### Docker

1. **Build the image**
   ```bash
   docker build -t ocr-app .
   ```

2. **Run the container**
   ```bash
   docker run -p 8080:8080 \
     -e APP_USERNAME=your_username \
     -e APP_PASSWORD=your_password \
     ocr-app
   ```

   The app will be available at `http://localhost:8080`

## GCP Cloud Run Deployment

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured  

  *Alternatively*, you can use the Google Cloud Web Terminal ("Activate Cloud Shell") in the GCP Console to set up and manage the Cloud infrastructure directly, without requiring a local SDK install.

- A GCP project with billing enabled
- Required APIs enabled: Cloud Run, Cloud Build, Artifact Registry, Secret Manager




### Step 1: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```



### Step 2: Create Artifact Registry Repository

```bash
gcloud artifacts repositories create ocr-app-repo \
  --repository-format=docker \
  --location=us-east1 \
  --description="Docker repository for OCR app"
```

### Step 2.5: (If using GCP Cloud Shell) Clone the Repository

If you're running these steps inside the [GCP Cloud Shell](https://cloud.google.com/shell), first clone your repository and change into its directory:

```bash
git clone https://github.com/RutanshuDesai/ocr_to_text_app.git
cd ocr_to_text_app
```
_Now continue with the **Build and Push the Image** step below from inside the cloned directory._


### Step 3: Build and Push the Image

```bash
gcloud builds submit \
  --tag us-east1-docker.pkg.dev/YOUR_PROJECT_ID/ocr-app-repo/ocr-app .
```

### Step 4: Create Secrets in Secret Manager

```bash
# Create secrets
echo -n "your_username" | gcloud secrets create APP_USERNAME --data-file=-
echo -n "your_secure_password" | gcloud secrets create APP_PASSWORD --data-file=-
```

### Step 5: Grant Secret Access to Cloud Run

Get your project number:
```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')
```

Grant access:
```bash
gcloud secrets add-iam-policy-binding APP_USERNAME \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding APP_PASSWORD \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 6: Deploy to Cloud Run

```bash
gcloud run deploy ocr-service \
  --image us-east1-docker.pkg.dev/YOUR_PROJECT_ID/ocr-app-repo/ocr-app \
  --region us-east1 \
  --allow-unauthenticated \
  --max-instances 1 \
  --memory 1Gi \
  --cpu 1 \
  --set-secrets=APP_USERNAME=APP_USERNAME:latest,APP_PASSWORD=APP_PASSWORD:latest
```

### Step 7: Access Your Application

After deployment, Cloud Run will provide a URL like:
```
https://ocr-service-xxxxx-ue.a.run.app
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_USERNAME` | Username for app authentication | Yes |
| `APP_PASSWORD` | Password for app authentication | Yes |

### Supported Languages

The default language is Gujarati (`guj`). To use other languages:

1. **Local/Docker**: Install the appropriate Tesseract language pack
2. **Enter the language code** in the app's "Tesseract language code" field

Common language codes:
- `eng` - English
- `hin` - Hindi
- `guj` - Gujarati
- `mar` - Marathi
- `tam` - Tamil
- `tel` - Telugu

Full list: [Tesseract Languages](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)

### Adding Language Support in Docker

Edit the `Dockerfile` to include additional languages:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr \
       tesseract-ocr-guj \
       tesseract-ocr-hin \
       tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*
```

## Project Structure

```
pdf-translation-business/
├── app.py              # Streamlit web application
├── translation.py      # OCR processing logic
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── env-example         # Example environment file
├── sample_cloud_run.sh # GCP deployment reference commands
└── LICENSE             # MIT License
```

## Cost Considerations (GCP)

Cloud Run charges based on usage:
- **CPU**: Charged per vCPU-second while processing requests
- **Memory**: Charged per GiB-second while processing requests
- **Requests**: First 2 million requests/month are free

With `--max-instances 1` and typical usage, monthly costs are often under $5.

See [Cloud Run Pricing](https://cloud.google.com/run/pricing) for details.



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Open source OCR engine
- [Streamlit](https://streamlit.io/) - Web framework for data apps
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library
