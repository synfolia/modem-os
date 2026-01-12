"""
Unit tests for configuration management.

Tests the Config class and configuration loading.
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration loading and access."""

    def test_config_defaults(self):
        """Test that default configuration loads when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "nonexistent.yaml")
            config = Config(config_path)

            # Check defaults are loaded
            self.assertEqual(config.ollama_model, "deepseek-r1:latest")
            self.assertEqual(config.dashboard_port, 8080)
            self.assertIsInstance(config.genetic_markers, list)

    def test_config_get_method(self):
        """Test the get() method for accessing config values."""
        config = Config("config.yaml")

        # Test nested access
        model = config.get("ollama.model")
        self.assertIsNotNone(model)

        # Test default value
        missing = config.get("nonexistent.key", "default_value")
        self.assertEqual(missing, "default_value")

    def test_ollama_url_property(self):
        """Test that ollama_url is properly formatted."""
        config = Config("config.yaml")
        url = config.ollama_url

        self.assertIn("http://", url)
        self.assertIn("/api/generate", url)

    def test_scroll_engine_url_property(self):
        """Test that scroll_engine_url is properly formatted."""
        config = Config("config.yaml")
        url = config.scroll_engine_url

        self.assertIn("http://", url)
        self.assertIn("/simulate", url)

    def test_config_properties(self):
        """Test all configuration properties return valid values."""
        config = Config("config.yaml")

        # Test all properties return something
        self.assertIsNotNone(config.ollama_model)
        self.assertIsNotNone(config.ollama_timeout)
        self.assertIsNotNone(config.genetic_markers)
        self.assertIsNotNone(config.trust_threshold)
        self.assertIsNotNone(config.sap_num_proposals)
        self.assertIsNotNone(config.dashboard_host)
        self.assertIsNotNone(config.dashboard_port)
        self.assertIsNotNone(config.dashboard_max_workers)
        self.assertIsNotNone(config.trace_dir)
        self.assertIsNotNone(config.scroll_dir)

    def test_config_types(self):
        """Test that configuration values have correct types."""
        config = Config("config.yaml")

        # String types
        self.assertIsInstance(config.ollama_model, str)
        self.assertIsInstance(config.dashboard_host, str)

        # Integer types
        self.assertIsInstance(config.ollama_timeout, int)
        self.assertIsInstance(config.dashboard_port, int)
        self.assertIsInstance(config.dashboard_max_workers, int)

        # Float types
        self.assertIsInstance(config.trust_threshold, float)

        # List types
        self.assertIsInstance(config.genetic_markers, list)

    def test_config_with_custom_yaml(self):
        """Test loading configuration from custom YAML."""
        yaml_content = """
ollama:
  host: "test-host"
  port: 9999
  model: "test-model:latest"

dashboard:
  port: 5000
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.yaml")
            with open(config_path, 'w') as f:
                f.write(yaml_content)

            config = Config(config_path)

            # Check custom values
            self.assertEqual(config.get("ollama.host"), "test-host")
            self.assertEqual(config.get("ollama.port"), 9999)
            self.assertEqual(config.ollama_model, "test-model:latest")
            self.assertEqual(config.dashboard_port, 5000)

            # Check that defaults fill in missing values
            self.assertIsNotNone(config.genetic_markers)


class TestConfigSingleton(unittest.TestCase):
    """Test the get_config() singleton function."""

    def test_get_config(self):
        """Test that get_config returns a Config instance."""
        from core.config import get_config

        config = get_config()
        self.assertIsInstance(config, Config)

    def test_config_singleton(self):
        """Test that get_config returns the same instance."""
        from core.config import get_config, reload_config

        # Reload to start fresh
        reload_config()

        config1 = get_config()
        config2 = get_config()

        # Should be the same instance
        self.assertIs(config1, config2)

    def test_reload_config(self):
        """Test that reload_config creates a new instance."""
        from core.config import get_config, reload_config

        config1 = get_config()
        reload_config()
        config2 = get_config()

        # Should be different instances (reload creates new)
        self.assertIsNot(config1, config2)


if __name__ == "__main__":
    unittest.main()
