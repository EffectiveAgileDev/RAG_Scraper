"""Unit tests for text file configuration manager."""
import os
import tempfile
import json

import pytest

from src.file_generator.text_file_generator import TextFileConfig, TextFileConfigManager


class TestTextFileConfigManager:
    """Test suite for TextFileConfigManager."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for config files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create TextFileConfigManager instance."""
        config_file = os.path.join(temp_config_dir, "test_config.json")
        return TextFileConfigManager(config_file)
    
    def test_save_and_load_config(self, config_manager, temp_config_dir):
        """Test saving and loading configuration."""
        # Create config to save
        original_config = TextFileConfig(
            output_directory=temp_config_dir,
            allow_overwrite=False,
            encoding="utf-8",
            filename_pattern="Custom_{timestamp}.txt"
        )
        
        # Save config
        config_manager.save_config(original_config)
        
        # Load config
        loaded_config = config_manager.load_config()
        
        # Verify loaded config matches original
        assert loaded_config is not None
        assert loaded_config.output_directory == original_config.output_directory
        assert loaded_config.allow_overwrite == original_config.allow_overwrite
        assert loaded_config.encoding == original_config.encoding
        assert loaded_config.filename_pattern == original_config.filename_pattern
    
    def test_load_nonexistent_config_returns_none(self, config_manager):
        """Test loading nonexistent config returns None."""
        loaded_config = config_manager.load_config()
        assert loaded_config is None
    
    def test_load_corrupted_config_returns_none(self, config_manager, temp_config_dir):
        """Test loading corrupted config returns None."""
        # Create corrupted config file
        config_file = os.path.join(temp_config_dir, "test_config.json")
        with open(config_file, 'w') as f:
            f.write("invalid json content")
        
        loaded_config = config_manager.load_config()
        assert loaded_config is None
    
    def test_get_or_create_config_creates_default(self, config_manager, temp_config_dir):
        """Test get_or_create_config creates default when no config exists."""
        config = config_manager.get_or_create_config(temp_config_dir)
        
        # Verify default config was created
        assert config.output_directory == temp_config_dir
        assert config.allow_overwrite is True
        assert config.encoding == "utf-8"
        assert config.filename_pattern == "WebScrape_{timestamp}.txt"
        
        # Verify config was saved
        assert os.path.exists(config_manager.config_file)
    
    def test_get_or_create_config_loads_existing(self, config_manager, temp_config_dir):
        """Test get_or_create_config loads existing config."""
        # Create custom directory that can actually be created
        custom_dir = os.path.join(temp_config_dir, "custom_path")
        os.makedirs(custom_dir, exist_ok=True)
        
        # Create and save initial config
        original_config = TextFileConfig(
            output_directory=custom_dir,
            allow_overwrite=False
        )
        config_manager.save_config(original_config)
        
        # Get config (should load existing)
        loaded_config = config_manager.get_or_create_config(temp_config_dir)
        
        # Verify existing config was loaded (not default)
        assert loaded_config.output_directory == custom_dir
        assert loaded_config.allow_overwrite is False
    
    def test_config_file_format(self, config_manager, temp_config_dir):
        """Test config file format is correct JSON."""
        config = TextFileConfig(
            output_directory=temp_config_dir,
            allow_overwrite=True,
            encoding="utf-8",
            filename_pattern="Test_{timestamp}.txt"
        )
        
        config_manager.save_config(config)
        
        # Read raw config file
        with open(config_manager.config_file, 'r') as f:
            saved_data = json.load(f)
        
        # Verify JSON structure
        expected_keys = {'output_directory', 'allow_overwrite', 'encoding', 'filename_pattern'}
        assert set(saved_data.keys()) == expected_keys
        
        assert saved_data['output_directory'] == temp_config_dir
        assert saved_data['allow_overwrite'] is True
        assert saved_data['encoding'] == "utf-8"
        assert saved_data['filename_pattern'] == "Test_{timestamp}.txt"
    
    def test_persistent_directory_preference(self, config_manager, temp_config_dir):
        """Test that directory preference persists across sessions."""
        custom_dir = os.path.join(temp_config_dir, "custom_output")
        os.makedirs(custom_dir, exist_ok=True)
        
        # Save config with custom directory
        config = TextFileConfig(output_directory=custom_dir)
        config_manager.save_config(config)
        
        # Simulate application restart by creating new config manager
        new_manager = TextFileConfigManager(config_manager.config_file)
        loaded_config = new_manager.load_config()
        
        # Verify directory preference was restored
        assert loaded_config.output_directory == custom_dir
    
    def test_config_validation_on_load(self, config_manager, temp_config_dir):
        """Test config validation when loading."""
        # Create config with missing fields
        incomplete_config = {
            'output_directory': temp_config_dir,
            'allow_overwrite': True
            # Missing encoding and filename_pattern
        }
        
        with open(config_manager.config_file, 'w') as f:
            json.dump(incomplete_config, f)
        
        # Should handle missing fields gracefully by using defaults
        loaded_config = config_manager.load_config()
        # The TextFileConfig should use defaults for missing fields
        assert loaded_config is not None
        assert loaded_config.output_directory == temp_config_dir
        assert loaded_config.allow_overwrite is True
        assert loaded_config.encoding == "utf-8"  # Default value
        assert loaded_config.filename_pattern == "WebScrape_{timestamp}.txt"  # Default value
    
    def test_config_manager_with_custom_filename(self, temp_config_dir):
        """Test config manager with custom config filename."""
        custom_config_file = os.path.join(temp_config_dir, "my_custom_config.json")
        manager = TextFileConfigManager(custom_config_file)
        
        config = TextFileConfig(output_directory=temp_config_dir)
        manager.save_config(config)
        
        # Verify custom config file was created
        assert os.path.exists(custom_config_file)
        
        # Verify config can be loaded
        loaded_config = manager.load_config()
        assert loaded_config is not None
        assert loaded_config.output_directory == temp_config_dir


class TestConfigPersistenceIntegration:
    """Integration tests for config persistence scenarios."""
    
    def test_application_restart_scenario(self):
        """Test full application restart scenario with config persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "app_config.json")
            output_dir = os.path.join(temp_dir, "restaurant_data")
            os.makedirs(output_dir, exist_ok=True)
            
            # Session 1: User configures custom directory
            session1_manager = TextFileConfigManager(config_file)
            user_config = TextFileConfig(
                output_directory=output_dir,
                allow_overwrite=False
            )
            session1_manager.save_config(user_config)
            
            # Verify config was saved
            assert os.path.exists(config_file)
            
            # Session 2: Application restart, should restore user preference
            session2_manager = TextFileConfigManager(config_file)
            restored_config = session2_manager.load_config()
            
            # Verify user preference was restored
            assert restored_config is not None
            assert restored_config.output_directory == output_dir
            assert restored_config.allow_overwrite is False
    
    def test_first_time_user_experience(self):
        """Test first-time user experience with default config creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "new_user_config.json")
            default_output_dir = os.path.join(temp_dir, "default_output")
            
            # New user starts app (no config exists)
            manager = TextFileConfigManager(config_file)
            
            # App creates default config
            config = manager.get_or_create_config(default_output_dir)
            
            # Verify default config was created and saved
            assert config.output_directory == default_output_dir
            assert os.path.exists(config_file)
            
            # Verify config can be loaded in future sessions
            loaded_config = manager.load_config()
            assert loaded_config.output_directory == default_output_dir