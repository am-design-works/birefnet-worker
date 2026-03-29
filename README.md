# BiRefNet Background Removal Worker

Lightweight RunPod serverless worker for high-quality background removal using BiRefNet.

## Features

- **BiRefNet-General** - State-of-the-art background removal
- **GPU Accelerated** - Fast inference on NVIDIA GPUs
- **Alpha Matting** - Clean edges with transparency refinement
- **URL or Base64 Input** - Flexible image input options
- **~2-3s Cold Start** - Lightweight compared to full ComfyUI workers

## Deploy to RunPod

### Step 1: Push to GitHub

Create a new GitHub repo (e.g., `birefnet-worker`) and push these files.

### Step 2: Create RunPod Endpoint

1. Go to [RunPod Serverless](https://runpod.io/console/serverless)
2. Click **"+ New Endpoint"**
3. Select **"Custom Source"** → **"Build from GitHub"**
4. Enter your GitHub repo URL
5. Configure:
   - **GPU Type**: RTX 3090 / RTX 4000 Ada / A4000 (16GB+ VRAM)
   - **Active Workers**: 0
   - **Max Workers**: 2
   - **Idle Timeout**: 5 seconds
   - **Execution Timeout**: 300 seconds
6. Click **Create**

Build time: ~5-10 minutes (downloading models)

### Step 3: Get Endpoint ID

After deployment, copy the **Endpoint ID** from the dashboard (e.g., `abc123def456`).

### Step 4: Add to Environment

Add these to your `.env` / `.env.local`:

```bash
RUNPOD_API_KEY=your_runpod_api_key
RUNPOD_BIREFNET_ENDPOINT_ID=your_endpoint_id
```

## API Usage

### Remove Background (URL)

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "url": "https://example.com/image.jpg"
    }
  }' \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

### Remove Background (Base64)

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "image": "BASE64_ENCODED_IMAGE"
    }
  }' \
  https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

### Response

```json
{
  "id": "job-id",
  "status": "COMPLETED",
  "output": {
    "image": "BASE64_PNG_WITH_TRANSPARENT_BG",
    "width": 1920,
    "height": 1080,
    "model": "birefnet-general"
  }
}
```

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | - | Public URL of image to process |
| `image` | string | - | Base64-encoded image (alternative to url) |
| `model` | string | `birefnet-general` | Model: `birefnet-general` or `u2net` |
| `alpha_matting` | boolean | `true` | Enable alpha matting for better edges |

## GPU Requirements

| GPU | VRAM | Status |
|-----|------|--------|
| RTX 3090 | 24GB | ✅ Recommended |
| RTX 4000 Ada | 20GB | ✅ Works |
| A4000 | 16GB | ✅ Works |
| RTX 4090 | 24GB | ✅ Best |
| A5000 | 24GB | ✅ Best |

**Minimum VRAM**: 12GB (BiRefNet ONNX requires ~8GB)

## Estimated Costs

- **Cold start**: ~2-3 seconds
- **Inference time**: ~1-3 seconds per image
- **Cost per image**: ~$0.002-0.005 (RTX 3090)

## Local Development

```bash
# Build
docker build -t birefnet-worker .

# Run (requires NVIDIA GPU)
docker run --gpus all -p 8000:8000 birefnet-worker

# Test
curl -X POST http://localhost:8000/runsync \
  -H "Content-Type: application/json" \
  -d '{"input": {"url": "https://example.com/image.jpg"}}'
```

## Troubleshooting

### "CUDA out of memory"
- Use a GPU with more VRAM (16GB+)
- Or resize large images before processing

### "Model download failed"
- The model is pre-downloaded in Docker build
- Check if Hugging Face is accessible during build

### Slow cold starts
- Increase **Active Workers** to 1 for always-warm
- Or use **Flash Boot** if available

## License

MIT License
