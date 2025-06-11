"""
Tests for CLI Interface 💻

Testing command-line interface functionality.
"""

import pytest
import tempfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, Mock

from codedoc.cli import cli, generate, parse, demo


class TestCLI:
    """Test CLI commands."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert '🚀 CodeDoc AI' in result.output
        assert 'Smart Documentation Generator' in result.output
        assert 'generate' in result.output
        assert 'parse' in result.output
        assert 'demo' in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert 'CodeDoc AI' in result.output
    
    def test_generate_command_help(self):
        """Test generate command help."""
        result = self.runner.invoke(generate, ['--help'])
        
        assert result.exit_code == 0
        assert 'Generate AI-powered documentation' in result.output
        assert '--output' in result.output
        assert '--format' in result.output
        assert '--no-ai' in result.output
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_generate_command_success(self, mock_generator):
        """Test successful documentation generation."""
        # Mock successful generation
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {
            'status': 'success',
            'functions_documented': 2,
            'classes_documented': 1,
            'ai_enhanced': False,
            'output_files': ['docs/documentation.html', 'docs/style.css']
        }
        mock_generator.return_value = mock_instance
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [
                temp_file,
                '--output', 'test_docs',
                '--format', 'html',
                '--no-ai'
            ])
            
            assert result.exit_code == 0
            assert '✅ Documentation generated successfully!' in result.output
            assert '2' in result.output  # functions count
            assert '1' in result.output  # classes count
            
            # Check that generator was called with correct parameters
            mock_generator.assert_called_once()
            mock_instance.generate_documentation.assert_called_once_with(
                source_path=temp_file,
                output_path='test_docs',
                format_type='html'
            )
            
        finally:
            Path(temp_file).unlink()
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_generate_command_error(self, mock_generator):
        """Test error handling in generate command."""
        # Mock error
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {
            'status': 'error',
            'message': 'No code elements found'
        }
        mock_generator.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('# Empty file')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--no-ai'])
            
            assert result.exit_code == 0  # CLI doesn't exit with error code for business logic errors
            assert '❌ Error:' in result.output
            assert 'No code elements found' in result.output
            
        finally:
            Path(temp_file).unlink()
    
    def test_generate_command_missing_file(self):
        """Test generate command with non-existent file."""
        result = self.runner.invoke(generate, ['nonexistent.py'])
        
        assert result.exit_code == 2  # Click error for missing file
        assert 'does not exist' in result.output.lower()
    
    def test_generate_command_api_key_warning(self):
        """Test API key warning when AI is enabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            # Run without API key and without --no-ai flag
            with patch.dict('os.environ', {}, clear=True):
                result = self.runner.invoke(generate, [temp_file])
                
                assert '⚠️  No OpenAI API key found!' in result.output
                assert 'Continuing without AI features' in result.output
            
        finally:
            Path(temp_file).unlink()
    
    def test_parse_command_success(self):
        """Test successful parse command."""
        # Create a simple test file
        code = '''
def test_function():
    """A test function."""
    return True

class TestClass:
    """A test class."""
    def method(self):
        """A method."""
        pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = self.runner.invoke(parse, [temp_file])
            
            assert result.exit_code == 0
            assert 'Functions found:' in result.output
            assert 'Classes found:' in result.output
            
        finally:
            Path(temp_file).unlink()
    
    def test_parse_command_directory_error(self):
        """Test parse command with directory (should error)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.runner.invoke(parse, [temp_dir])
            
            assert result.exit_code == 0  # Doesn't abort, just prints message
            assert 'Directory parsing not implemented' in result.output
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_demo_command_success(self, mock_generator):
        """Test successful demo command."""
        # Mock successful demo
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {
            'status': 'success',
            'functions_documented': 3,
            'classes_documented': 2,
            'ai_enhanced': False,
            'output_files': ['demo_docs/documentation.html']
        }
        mock_generator.return_value = mock_instance
        
        result = self.runner.invoke(demo)
        
        assert result.exit_code == 0
        assert '🎭 CodeDoc AI - Demo Mode' in result.output
        assert '📝 Created demo file:' in result.output
        assert '🎉 Demo documentation generated successfully!' in result.output
        assert 'demo_docs/documentation.html' in result.output
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_demo_command_error(self, mock_generator):
        """Test demo command with generation error."""
        # Mock error
        mock_instance = Mock()
        mock_instance.generate_documentation.side_effect = Exception("Test error")
        mock_generator.return_value = mock_instance
        
        result = self.runner.invoke(demo)
        
        assert result.exit_code == 0  # Should handle error gracefully
        assert '❌ Demo failed:' in result.output
        assert 'Test error' in result.output
    
    def test_verbose_flag(self):
        """Test verbose flag functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('invalid python code that will cause error')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--verbose', '--no-ai'])
            
            # Should show more detailed error information when verbose
            if result.exit_code != 0:
                assert '--verbose' in result.output or 'traceback' in result.output.lower()
            
        finally:
            Path(temp_file).unlink()


class TestCLIFormats:
    """Test CLI format options."""
    
    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_html_format(self, mock_generator):
        """Test HTML format option."""
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {'status': 'success', 'functions_documented': 0, 'classes_documented': 0, 'ai_enhanced': False, 'output_files': []}
        mock_generator.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--format', 'html', '--no-ai'])
            
            mock_instance.generate_documentation.assert_called_once()
            call_args = mock_instance.generate_documentation.call_args
            assert call_args[1]['format_type'] == 'html'
            
        finally:
            Path(temp_file).unlink()
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_markdown_format(self, mock_generator):
        """Test Markdown format option."""
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {'status': 'success', 'functions_documented': 0, 'classes_documented': 0, 'ai_enhanced': False, 'output_files': []}
        mock_generator.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--format', 'markdown', '--no-ai'])
            
            call_args = mock_instance.generate_documentation.call_args
            assert call_args[1]['format_type'] == 'markdown'
            
        finally:
            Path(temp_file).unlink()
    
    @patch('codedoc.cli.DocumentationGenerator')
    def test_both_format(self, mock_generator):
        """Test both formats option."""
        mock_instance = Mock()
        mock_instance.generate_documentation.return_value = {'status': 'success', 'functions_documented': 0, 'classes_documented': 0, 'ai_enhanced': False, 'output_files': []}
        mock_generator.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--format', 'both', '--no-ai'])
            
            call_args = mock_instance.generate_documentation.call_args
            assert call_args[1]['format_type'] == 'both'
            
        finally:
            Path(temp_file).unlink()
    
    def test_invalid_format(self):
        """Test invalid format option."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def test(): pass')
            temp_file = f.name
        
        try:
            result = self.runner.invoke(generate, [temp_file, '--format', 'invalid'])
            
            assert result.exit_code == 2  # Click validation error
            assert 'Invalid value' in result.output
            
        finally:
            Path(temp_file).unlink() 