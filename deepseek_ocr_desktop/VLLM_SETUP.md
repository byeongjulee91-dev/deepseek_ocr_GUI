# vLLM Remote Inference Setup Guide

This guide explains how to use vLLM remote inference with DeepSeek-OCR Desktop Application.

## What is vLLM Mode?

vLLM mode allows you to use a remote vLLM server for OCR inference instead of loading the model locally. This is useful when:

- You want to run the desktop app on a machine without a GPU
- You have a shared vLLM server for multiple users
- You want to save VRAM on your local machine
- You need faster startup times (no model loading)

## Prerequisites

### 1. Install and Start vLLM Server

On your server machine (with GPU), install and start vLLM:

```bash
# Install vLLM
pip install vllm

# Start vLLM server with DeepSeek-OCR model
vllm serve deepseek-ai/DeepSeek-OCR \
  --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor \
  --no-enable-prefix-caching \
  --mm-processor-cache-gb 0
```

**Note**: The vLLM server will be available at `http://localhost:8000/v1` by default.

For more details, see: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR.html

### 2. Install OpenAI Package (Desktop App)

The desktop app uses the OpenAI Python client to communicate with vLLM:

```bash
cd deepseek_ocr_desktop
uv pip install openai
# or
pip install openai>=1.0.0
```

This is already included in `requirements.txt` if you install fresh.

## Configuration

### Option 1: Settings Dialog (GUI)

1. Open the desktop application
2. Go to **Settings** (Ctrl+,) or click the gear icon
3. Navigate to the **🤖 Model** tab
4. In the **vLLM Remote Inference** section:
   - ✅ Check "Use vLLM remote endpoint instead of local model"
   - Enter your vLLM endpoint URL (e.g., `http://localhost:8000/v1`)
   - Optionally enter an API key if your server requires authentication
5. Click **💾 Save**
6. **Restart the application** for changes to take effect

### Option 2: Manual Configuration

vLLM settings are stored in QSettings:

- **Linux**: `~/.config/DeepSeekOCR/DesktopApp.conf`
- **Windows**: Registry at `HKEY_CURRENT_USER\Software\DeepSeekOCR\DesktopApp`
- **macOS**: `~/Library/Preferences/com.DeepSeekOCR.DesktopApp.plist`

Example configuration (INI format for Linux):

```ini
[vllm]
use_vllm=true
endpoint=http://localhost:8000/v1
api_key=
```

## Usage

Once configured, the desktop app will:

1. **Connect to vLLM** on startup instead of loading the local model
2. **Send images** to the remote server for OCR processing
3. **Receive results** just like local mode

All features work identically in both modes:
- ✅ Image OCR (all modes: plain_ocr, describe, find_ref, freeform)
- ✅ PDF processing (all output formats: markdown, html, docx, json)
- ✅ Bounding box detection (find_ref mode)
- ✅ Image extraction from PDFs

## Network Setup

### Local Network

If the vLLM server is on the same machine:
```
Endpoint: http://localhost:8000/v1
```

If the vLLM server is on another machine in your local network:
```
Endpoint: http://192.168.1.100:8000/v1
```

### Remote Server

If using a remote server, ensure:
1. The vLLM server is accessible over the network
2. Firewall allows port 8000 (or your configured port)
3. Use HTTPS for production: `https://your-server.com/v1`

## Health Check

The desktop app provides two ways to check vLLM connection health:

### 1. Test Connection in Settings Dialog

1. Open **Settings** (Ctrl+,)
2. Go to **🤖 Model** tab
3. Enable vLLM and enter endpoint URL
4. Click **🔍 Test Connection** button
5. View connection status in dialog

This tests the connection **before** saving settings, allowing you to verify the endpoint is correct.

### 2. Check Connection from Help Menu

When vLLM is already configured:

1. Go to **Help** menu
2. Select **Check vLLM Connection**
3. View health check result

This checks the **currently configured** endpoint and shows:
- ✅ Connection status
- 📍 Endpoint URL
- 🤖 Model name
- 📊 Available models on server

**Tip**: Use this regularly to ensure your vLLM server is healthy!

## Troubleshooting

### Connection Errors

**Error**: "Failed to connect to vLLM endpoint"

**Solutions**:
1. **Use Health Check**: Go to Help → Check vLLM Connection for detailed error
2. Verify the vLLM server is running:
   ```bash
   curl http://localhost:8000/v1/models
   ```
3. Check the endpoint URL in settings (must end with `/v1`)
4. Check firewall settings
5. Review logs in the desktop app's Log Viewer tab

### Model Not Found

**Error**: "Connected but model not found"

**Solution**: Ensure the vLLM server was started with the correct model:
```bash
vllm serve deepseek-ai/DeepSeek-OCR ...
```

The model name in desktop app settings must match the vLLM server model.

### Slow Performance

If inference is slower than expected:
1. Check network latency (use `ping` to test)
2. Ensure vLLM server has adequate GPU resources
3. Check vLLM server logs for bottlenecks
4. Consider using a local model if latency is too high

## Switching Between Local and vLLM

You can switch between local and vLLM modes at any time:

1. Open **Settings** (Ctrl+,)
2. Go to **🤖 Model** tab
3. Toggle "Use vLLM remote endpoint"
4. **Save** and **restart** the application

**Note**: Model settings (HF_HOME, model name) are only used in local mode.

## Performance Comparison

| Aspect | Local Mode | vLLM Mode |
|--------|-----------|-----------|
| Startup Time | 10-30 seconds | 1-2 seconds |
| VRAM Usage | 8-12 GB | 0 GB (client) |
| Inference Speed | Fast (local GPU) | Depends on network |
| Network Required | No | Yes |
| Multi-user | No | Yes (server) |

## Security Considerations

- **API Keys**: Use API keys if your vLLM server requires authentication
- **HTTPS**: Use HTTPS endpoints for production environments
- **Network**: Restrict vLLM server access to trusted networks only
- **Credentials**: The desktop app stores API keys in QSettings (encrypted on some platforms)

## Advanced: Docker Deployment

To deploy vLLM server with Docker:

```bash
docker run --gpus all -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model deepseek-ai/DeepSeek-OCR \
  --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor \
  --no-enable-prefix-caching \
  --mm-processor-cache-gb 0
```

Then configure the desktop app to use `http://localhost:8000/v1`.

## FAQ

**Q: Can I use vLLM mode without a GPU on the client machine?**
A: Yes! vLLM mode doesn't require a GPU on the client. Only the vLLM server needs a GPU.

**Q: Does vLLM mode support all OCR features?**
A: Yes, all features work identically in both local and vLLM modes.

**Q: Can multiple users share one vLLM server?**
A: Yes, vLLM supports concurrent requests from multiple clients.

**Q: What happens if the vLLM server goes down?**
A: The desktop app will show connection errors. Switch back to local mode in settings.

**Q: Is there any data sent to the internet?**
A: No, unless your vLLM endpoint is on the internet. By default, everything runs locally.

## References

- vLLM Documentation: https://docs.vllm.ai/
- DeepSeek-OCR vLLM Recipe: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR.html
- OpenAI Python Client: https://github.com/openai/openai-python
