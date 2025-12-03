"""
Application Configuration Manager
Wraps QSettings for persistent configuration storage
"""

import os
from PySide6.QtCore import QSettings


class AppConfig:
    """Application configuration manager using QSettings"""

    def __init__(self):
        """Initialize settings with organization and application name"""
        self.settings = QSettings("DeepSeekOCR", "DesktopApp")

    # Model Configuration
    def get_model_name(self) -> str:
        """Get HuggingFace model name"""
        return self.settings.value("model/name", "deepseek-ai/DeepSeek-OCR")

    def set_model_name(self, name: str):
        """Set HuggingFace model name"""
        self.settings.setValue("model/name", name)

    def get_hf_home(self) -> str:
        """Get HuggingFace cache directory"""
        default = os.path.expanduser("~/.cache/huggingface")
        return self.settings.value("model/hf_home", default)

    def set_hf_home(self, path: str):
        """Set HuggingFace cache directory"""
        self.settings.setValue("model/hf_home", path)

    # vLLM Configuration
    def get_use_vllm(self) -> bool:
        """Get whether to use vLLM remote endpoint instead of local model"""
        return self.settings.value("vllm/use_vllm", False, type=bool)

    def set_use_vllm(self, enabled: bool):
        """Set whether to use vLLM remote endpoint"""
        self.settings.setValue("vllm/use_vllm", enabled)

    def get_vllm_endpoint(self) -> str:
        """Get vLLM endpoint URL"""
        return self.settings.value("vllm/endpoint", "http://localhost:8000/v1")

    def set_vllm_endpoint(self, endpoint: str):
        """Set vLLM endpoint URL"""
        self.settings.setValue("vllm/endpoint", endpoint)

    def get_vllm_api_key(self) -> str:
        """Get vLLM API key (optional)"""
        return self.settings.value("vllm/api_key", "")

    def set_vllm_api_key(self, api_key: str):
        """Set vLLM API key"""
        self.settings.setValue("vllm/api_key", api_key)

    # Processing Configuration
    def get_base_size(self) -> int:
        """Get base processing size"""
        return self.settings.value("processing/base_size", 1024, type=int)

    def set_base_size(self, size: int):
        """Set base processing size"""
        self.settings.setValue("processing/base_size", size)

    def get_image_size(self) -> int:
        """Get image processing size"""
        return self.settings.value("processing/image_size", 640, type=int)

    def set_image_size(self, size: int):
        """Set image processing size"""
        self.settings.setValue("processing/image_size", size)

    def get_crop_mode(self) -> bool:
        """Get crop mode setting"""
        return self.settings.value("processing/crop_mode", True, type=bool)

    def set_crop_mode(self, enabled: bool):
        """Set crop mode setting"""
        self.settings.setValue("processing/crop_mode", enabled)

    # PDF Processing Configuration
    def get_pdf_dpi(self) -> int:
        """Get PDF rendering DPI"""
        return self.settings.value("pdf/dpi", 144, type=int)

    def set_pdf_dpi(self, dpi: int):
        """Set PDF rendering DPI"""
        self.settings.setValue("pdf/dpi", dpi)

    def get_extract_images(self) -> bool:
        """Get extract images from PDF setting"""
        return self.settings.value("pdf/extract_images", True, type=bool)

    def set_extract_images(self, enabled: bool):
        """Set extract images from PDF setting"""
        self.settings.setValue("pdf/extract_images", enabled)

    def get_pdf_extract_images(self) -> bool:
        """Get extract images from PDF setting (alias for consistency)"""
        return self.get_extract_images()

    def set_pdf_extract_images(self, enabled: bool):
        """Set extract images from PDF setting (alias for consistency)"""
        self.set_extract_images(enabled)

    # UI Configuration
    def get_last_directory(self) -> str:
        """Get last used directory for file dialogs"""
        default = os.path.expanduser("~")
        return self.settings.value("ui/last_directory", default)

    def set_last_directory(self, path: str):
        """Set last used directory for file dialogs"""
        self.settings.setValue("ui/last_directory", path)

    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.settings.value("ui/window_geometry")

    def set_window_geometry(self, geometry):
        """Save window geometry"""
        self.settings.setValue("ui/window_geometry", geometry)

    def get_window_state(self):
        """Get saved window state"""
        return self.settings.value("ui/window_state")

    def set_window_state(self, state):
        """Save window state"""
        self.settings.setValue("ui/window_state", state)

    def get_splitter_state(self):
        """Get saved splitter state"""
        return self.settings.value("ui/splitter_state")

    def set_splitter_state(self, state):
        """Save splitter state"""
        self.settings.setValue("ui/splitter_state", state)

    # Font Size Configuration
    def get_font_size(self) -> int:
        """Get application font size for result viewer"""
        return self.settings.value("ui/font_size", 12, type=int)

    def set_font_size(self, size: int):
        """Set application font size for result viewer"""
        self.settings.setValue("ui/font_size", size)

    def get_log_font_size(self) -> int:
        """Get font size for log viewer"""
        return self.settings.value("ui/log_font_size", 11, type=int)

    def set_log_font_size(self, size: int):
        """Set font size for log viewer"""
        self.settings.setValue("ui/log_font_size", size)

    def get_ui_font_size(self) -> int:
        """Get font size for UI elements (Control Panel, buttons, labels)"""
        return self.settings.value("ui/ui_font_size", 12, type=int)

    def set_ui_font_size(self, size: int):
        """Set font size for UI elements"""
        self.settings.setValue("ui/ui_font_size", size)

    # Advanced Settings
    def get_include_caption(self) -> bool:
        """Get include caption setting"""
        return self.settings.value("advanced/include_caption", False, type=bool)

    def set_include_caption(self, enabled: bool):
        """Set include caption setting"""
        self.settings.setValue("advanced/include_caption", enabled)

    def get_test_compress(self) -> bool:
        """Get test compress setting"""
        return self.settings.value("advanced/test_compress", False, type=bool)

    def set_test_compress(self, enabled: bool):
        """Set test compress setting"""
        self.settings.setValue("advanced/test_compress", enabled)

    # Clear all settings
    def clear_all(self):
        """Clear all settings"""
        self.settings.clear()

    def sync(self):
        """Force write settings to disk"""
        self.settings.sync()
