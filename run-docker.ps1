$ErrorActionPreference = "Stop"

$image = "fundamental-analysis-agent:latest"
$container = "fundamental-analysis-agent"

# Ensure the script runs from the project directory
Set-Location $PSScriptRoot

# Check required files
if (-not (Test-Path ".env")) {
    throw ".env file not found in $PSScriptRoot"
}

if (-not (Test-Path "Dockerfile")) {
    throw "Dockerfile not found in $PSScriptRoot"
}

# Build the latest image
docker build -t $image .

if ($LASTEXITCODE -ne 0) {
    throw "Docker build failed."
}

# Remove an existing container with the same name, if present
docker rm -f $container 2>$null | Out-Null

# Start the container
docker run --rm `
    --name $container `
    -p 8501:8501 `
    --env-file ".env" `
    $image

if ($LASTEXITCODE -ne 0) {
    throw "Docker container exited with an error."
}