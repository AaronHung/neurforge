# ruff: noqa
import os

# NEURFORGE_* env var aliases — map new names to legacy UTU_* names.
# Set NEURFORGE_* vars and they'll be forwarded automatically.
_NEURFORGE_ALIAS_MAP = {
    "NEURFORGE_LLM_TYPE": "UTU_LLM_TYPE",
    "NEURFORGE_LLM_MODEL": "UTU_LLM_MODEL",
    "NEURFORGE_LLM_BASE_URL": "UTU_LLM_BASE_URL",
    "NEURFORGE_LLM_API_KEY": "UTU_LLM_API_KEY",
    "NEURFORGE_IMAGE_LLM_TYPE": "UTU_IMAGE_LLM_TYPE",
    "NEURFORGE_IMAGE_LLM_MODEL": "UTU_IMAGE_LLM_MODEL",
    "NEURFORGE_IMAGE_LLM_BASE_URL": "UTU_IMAGE_LLM_BASE_URL",
    "NEURFORGE_IMAGE_LLM_API_KEY": "UTU_IMAGE_LLM_API_KEY",
    "NEURFORGE_AUDIO_LLM_TYPE": "UTU_AUDIO_LLM_TYPE",
    "NEURFORGE_AUDIO_LLM_MODEL": "UTU_AUDIO_LLM_MODEL",
    "NEURFORGE_AUDIO_LLM_BASE_URL": "UTU_AUDIO_LLM_BASE_URL",
    "NEURFORGE_AUDIO_LLM_API_KEY": "UTU_AUDIO_LLM_API_KEY",
    "NEURFORGE_DISABLE_TOOL_CACHE": "UTU_DISABLE_TOOL_CACHE",
    "NEURFORGE_DB_URL": "UTU_DB_URL",
    "NEURFORGE_LOG_LEVEL": "UTU_LOG_LEVEL",
    "NEURFORGE_WEBUI_PORT": "UTU_WEBUI_PORT",
    "NEURFORGE_WEBUI_IP": "UTU_WEBUI_IP",
    "NEURFORGE_WEBUI_AUTOLOAD": "UTU_WEBUI_AUTOLOAD",
    "NEURFORGE_WEBUI_WORKSPACE_ROOT": "UTU_WEBUI_WORKSPACE_ROOT",
}
for _new, _old in _NEURFORGE_ALIAS_MAP.items():
    if _new in os.environ and _old not in os.environ:
        os.environ[_old] = os.environ[_new]

from .utils import EnvUtils, setup_logging
from .tracing import setup_tracing

EnvUtils.assert_env(["UTU_LLM_TYPE", "UTU_LLM_MODEL"])
setup_logging(EnvUtils.get_env("UTU_LOG_LEVEL", "WARNING"))
setup_tracing()
