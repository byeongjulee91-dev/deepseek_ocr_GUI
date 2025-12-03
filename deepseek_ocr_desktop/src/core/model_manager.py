"""
Model Manager for DeepSeek OCR
Handles model loading in background thread with progress signals
Supports both local transformer model and remote vLLM endpoint
Adapted from backend/main.py lifespan function (lines 34-72)
"""

import os
from PySide6.QtCore import QThread, Signal, QObject
import torch
from transformers import AutoModel, AutoTokenizer

from .vllm_client import VLLMClient


class ModelLoadWorker(QThread):
    """Worker thread for loading the DeepSeek-OCR model or connecting to vLLM"""

    progress_signal = Signal(str)  # Progress message
    finished_signal = Signal(object, object)  # (model, tokenizer) or (vllm_client, None)
    error_signal = Signal(str)  # Error message

    def __init__(self, model_name: str, hf_home: str, use_vllm: bool = False,
                 vllm_endpoint: str = "", vllm_api_key: str = ""):
        """Initialize worker with model configuration

        Args:
            model_name: HuggingFace model identifier
            hf_home: HuggingFace cache directory
            use_vllm: Whether to use vLLM remote endpoint
            vllm_endpoint: vLLM endpoint URL
            vllm_api_key: vLLM API key (optional)
        """
        super().__init__()
        self.model_name = model_name
        self.hf_home = hf_home
        self.use_vllm = use_vllm
        self.vllm_endpoint = vllm_endpoint
        self.vllm_api_key = vllm_api_key

    def run(self):
        """Load model and tokenizer or connect to vLLM (runs in background thread)"""
        try:
            if self.use_vllm:
                # vLLM mode: Connect to remote endpoint
                self.progress_signal.emit(f"🌐 Connecting to vLLM endpoint: {self.vllm_endpoint}")

                # Create vLLM client
                vllm_client = VLLMClient(
                    endpoint=self.vllm_endpoint,
                    api_key=self.vllm_api_key if self.vllm_api_key else None,
                    model_name=self.model_name
                )

                # Test connection
                self.progress_signal.emit("🔍 Testing connection...")
                success, message = vllm_client.test_connection()

                if not success:
                    self.error_signal.emit(f"Failed to connect to vLLM endpoint:\n{message}")
                    return

                self.progress_signal.emit(message)
                self.progress_signal.emit("✅ vLLM client ready!")

                # Emit success with vLLM client (tokenizer is None for vLLM mode)
                self.finished_signal.emit(vllm_client, None)

            else:
                # Local mode: Load transformer model
                # Environment setup
                os.environ.pop("TRANSFORMERS_CACHE", None)
                os.makedirs(self.hf_home, exist_ok=True)
                os.environ["HF_HOME"] = self.hf_home

                self.progress_signal.emit(f"🚀 Loading local model: {self.model_name}")

                # Check CUDA availability
                if not torch.cuda.is_available():
                    self.error_signal.emit(
                        "CUDA is not available. This application requires an NVIDIA GPU with CUDA support."
                    )
                    return

                self.progress_signal.emit("📦 Loading tokenizer...")

                # Load tokenizer (fast)
                tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                )

                self.progress_signal.emit("🔧 Loading model (this may take 10-30 seconds)...")

                # Load model (slow, 5-30 seconds)
                torch_dtype = torch.bfloat16

                model = AutoModel.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    use_safetensors=True,
                    attn_implementation="eager",
                    torch_dtype=torch_dtype,
                ).eval().to("cuda")

                # Pad token setup
                try:
                    if getattr(tokenizer, "pad_token_id", None) is None and getattr(tokenizer, "eos_token_id", None) is not None:
                        tokenizer.pad_token = tokenizer.eos_token
                    if getattr(model.config, "pad_token_id", None) is None and getattr(tokenizer, "pad_token_id", None) is not None:
                        model.config.pad_token_id = tokenizer.pad_token_id
                except Exception:
                    pass

                self.progress_signal.emit("✅ Model loaded successfully!")

                # Emit success signal with model and tokenizer
                self.finished_signal.emit(model, tokenizer)

        except Exception as e:
            error_msg = f"Failed to initialize: {type(e).__name__}: {str(e)}"
            self.error_signal.emit(error_msg)


class ModelManager(QObject):
    """Manager for DeepSeek-OCR model with async loading (local or vLLM)"""

    model_loaded_signal = Signal(object, object)  # (model, tokenizer) or (vllm_client, None)
    load_progress_signal = Signal(str)  # Progress message
    load_error_signal = Signal(str)  # Error message

    def __init__(self):
        """Initialize model manager"""
        super().__init__()
        self.model = None
        self.tokenizer = None
        self.worker = None
        self.use_vllm = False

    def load_model_async(self, model_name: str, hf_home: str, use_vllm: bool = False,
                         vllm_endpoint: str = "", vllm_api_key: str = ""):
        """Start loading model asynchronously (local or vLLM)

        Args:
            model_name: HuggingFace model identifier
            hf_home: HuggingFace cache directory
            use_vllm: Whether to use vLLM remote endpoint
            vllm_endpoint: vLLM endpoint URL
            vllm_api_key: vLLM API key (optional)
        """
        self.use_vllm = use_vllm

        # Create worker thread
        self.worker = ModelLoadWorker(
            model_name,
            hf_home,
            use_vllm=use_vllm,
            vllm_endpoint=vllm_endpoint,
            vllm_api_key=vllm_api_key
        )

        # Connect signals
        self.worker.progress_signal.connect(self.load_progress_signal.emit)
        self.worker.finished_signal.connect(self._on_model_loaded)
        self.worker.error_signal.connect(self.load_error_signal.emit)

        # Start loading
        self.worker.start()

    def _on_model_loaded(self, model, tokenizer):
        """Handle model loaded successfully

        Args:
            model: Loaded DeepSeek-OCR model
            tokenizer: Loaded tokenizer
        """
        self.model = model
        self.tokenizer = tokenizer
        self.model_loaded_signal.emit(model, tokenizer)

        # Cleanup worker
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker = None

    def is_loaded(self) -> bool:
        """Check if model is loaded

        Returns:
            True if model and tokenizer are loaded
        """
        return self.model is not None and self.tokenizer is not None

    def get_model(self):
        """Get loaded model

        Returns:
            Loaded model or None
        """
        return self.model

    def get_tokenizer(self):
        """Get loaded tokenizer

        Returns:
            Loaded tokenizer or None
        """
        return self.tokenizer
