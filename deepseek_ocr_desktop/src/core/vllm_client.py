"""
vLLM Client for Remote DeepSeek OCR Inference
Uses OpenAI-compatible API to communicate with vLLM server
Based on: https://docs.vllm.ai/projects/recipes/en/latest/DeepSeek/DeepSeek-OCR.html
"""

import base64
from typing import Optional
from openai import OpenAI


class VLLMClient:
    """Client for vLLM remote inference using OpenAI-compatible API"""

    def __init__(self, endpoint: str, api_key: Optional[str] = None, model_name: str = "deepseek-ai/DeepSeek-OCR"):
        """Initialize vLLM client

        Args:
            endpoint: vLLM endpoint URL (e.g., "http://localhost:8000/v1")
            api_key: Optional API key for authentication
            model_name: Model name to use (default: "deepseek-ai/DeepSeek-OCR")
        """
        self.endpoint = endpoint
        self.model_name = model_name

        # Initialize OpenAI client with vLLM endpoint
        self.client = OpenAI(
            api_key=api_key or "EMPTY",  # vLLM doesn't require API key by default
            base_url=endpoint
        )

    def infer(
        self,
        prompt: str,
        image_file: str,
        base_size: int = 1024,  # noqa: ARG002 - kept for API compatibility
        image_size: int = 640,  # noqa: ARG002 - kept for API compatibility
        crop_mode: bool = True,  # noqa: ARG002 - kept for API compatibility
        **kwargs  # noqa: ARG002 - kept for API compatibility
    ) -> str:
        """Run OCR inference using vLLM endpoint

        Args:
            prompt: Text prompt for OCR
            image_file: Path to image file
            base_size: Base processing size (not used by vLLM, kept for compatibility)
            image_size: Image size parameter (not used by vLLM, kept for compatibility)
            crop_mode: Crop mode (not used by vLLM, kept for compatibility)
            **kwargs: Additional parameters (not used by vLLM, kept for compatibility)

        Returns:
            OCR result text

        Note:
            The base_size, image_size, crop_mode, and kwargs parameters are kept
            for API compatibility with the local model interface but are not used
            by vLLM. The vLLM server handles all image processing internally.
        """
        # Encode image to base64
        with open(image_file, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        # Build image URL (data URI)
        image_url = f"data:image/jpeg;base64,{image_data}"

        # Build messages array
        # Remove <image> tag from prompt as we're adding it as separate content
        text_prompt = prompt.replace("<image>", "").strip()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": text_prompt},
                ],
            }
        ]

        # Call vLLM API
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=2048,
            temperature=0.0,
            extra_body={
                "skip_special_tokens": False,
                "vllm_xargs": {
                    "ngram_size": 5,
                    "window_size": 10,
                    "whitelist_token_ids": [
                        32006,  # <|ref|>
                        32007,  # <|/ref|>
                        32008,  # <|det|>
                        32009,  # <|/det|>
                        32010,  # <|grounding|>
                    ],
                },
            },
        )

        # Extract text from response
        result_text = response.choices[0].message.content

        return result_text

    def test_connection(self) -> tuple[bool, str]:
        """Test connection to vLLM endpoint

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Try to list models
            models = self.client.models.list()
            model_names = [model.id for model in models.data]

            if self.model_name in model_names:
                return True, f"✅ Connected successfully. Model '{self.model_name}' is available."
            else:
                available = ", ".join(model_names[:3])
                return False, f"⚠️ Connected but model '{self.model_name}' not found. Available: {available}"

        except Exception as e:
            return False, f"❌ Connection failed: {type(e).__name__}: {str(e)}"
