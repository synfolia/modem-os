"""
Configuration management for MoDEM OS.

Loads settings from config.yaml and provides typed access to configuration values.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class Config:
    """Configuration loader and accessor for MoDEM OS."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.

        Args:
            config_path: Path to configuration file (default: config.yaml in project root)
        """
        self._config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file."""
        config_file = Path(self._config_path)

        if not config_file.exists():
            print(f"[WARNING] Config file not found: {self._config_path}")
            print("[WARNING] Using default configuration values")
            self._config = self._get_defaults()
            return

        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"[ERROR] Failed to parse config file: {e}")
            print("[WARNING] Using default configuration values")
            self._config = self._get_defaults()
        except Exception as e:
            print(f"[ERROR] Failed to load config file: {e}")
            print("[WARNING] Using default configuration values")
            self._config = self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        """Return default configuration values."""
        return {
            "ollama": {
                "host": "localhost",
                "port": 11434,
                "model": "deepseek-r1:latest",
                "timeout": 30
            },
            "scroll_engine": {
                "host": "localhost",
                "port": 8282,
                "timeout": 10
            },
            "genetic": {
                "markers": ["ATG16L1", "TNFSF15"],
                "trust_threshold": 0.7
            },
            "sap": {
                "num_proposals": 3,
                "scoring_weights": {
                    "plausibility": 1.0,
                    "utility": 1.0,
                    "novelty": 1.0,
                    "risk": 1.0,
                    "alignment": 1.0,
                    "efficiency": 1.0,
                    "resilience": 1.0
                }
            },
            "probe_suite": {
                "default_probe_count": 3,
                "include_control": True,
                "protocols": [
                    "conflict_stress",
                    "underspecification_stress",
                    "ambiguity_stress",
                    "safety_boundary"
                ]
            },
            "dashboard": {
                "host": "0.0.0.0",
                "port": 8080,
                "max_workers": 4
            },
            "storage": {
                "trace_dir": "core/research/trace_store",
                "scroll_dir": "scrolls/r_and_d/maria_lab/flare_trials"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.

        Args:
            key_path: Dot-separated path (e.g., "ollama.host")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    @property
    def ollama_url(self) -> str:
        """Get full Ollama API URL."""
        host = self.get("ollama.host", "localhost")
        port = self.get("ollama.port", 11434)
        return f"http://{host}:{port}/api/generate"

    @property
    def ollama_model(self) -> str:
        """Get Ollama model name."""
        return self.get("ollama.model", "deepseek-r1:latest")

    @property
    def ollama_timeout(self) -> int:
        """Get Ollama request timeout in seconds."""
        return self.get("ollama.timeout", 30)

    @property
    def scroll_engine_url(self) -> str:
        """Get full Scroll Engine API URL."""
        host = self.get("scroll_engine.host", "localhost")
        port = self.get("scroll_engine.port", 8282)
        return f"http://{host}:{port}/simulate"

    @property
    def scroll_engine_timeout(self) -> int:
        """Get Scroll Engine request timeout in seconds."""
        return self.get("scroll_engine.timeout", 10)

    @property
    def genetic_markers(self) -> List[str]:
        """Get genetic markers list."""
        return self.get("genetic.markers", ["ATG16L1", "TNFSF15"])

    @property
    def trust_threshold(self) -> float:
        """Get trust score threshold."""
        return self.get("genetic.trust_threshold", 0.7)

    @property
    def sap_num_proposals(self) -> int:
        """Get number of SAP proposals to generate."""
        return self.get("sap.num_proposals", 3)

    @property
    def dashboard_host(self) -> str:
        """Get dashboard host."""
        return self.get("dashboard.host", "0.0.0.0")

    @property
    def dashboard_port(self) -> int:
        """Get dashboard port."""
        return self.get("dashboard.port", 8080)

    @property
    def dashboard_max_workers(self) -> int:
        """Get dashboard thread pool max workers."""
        return self.get("dashboard.max_workers", 4)

    @property
    def trace_dir(self) -> str:
        """Get trace storage directory."""
        return self.get("storage.trace_dir", "core/research/trace_store")

    @property
    def scroll_dir(self) -> str:
        """Get scroll storage directory."""
        return self.get("storage.scroll_dir", "scrolls/r_and_d/maria_lab/flare_trials")


# Global configuration instance
_config_instance = None


def get_config() -> Config:
    """
    Get global configuration instance (singleton).

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """Reload configuration from file."""
    global _config_instance
    _config_instance = Config()
