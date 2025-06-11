"""
Tests for Core Documentation Generator 🚀

Testing the main orchestrator functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from codedoc.core import DocumentationGenerator
from codedoc.parser import FunctionInfo, ClassInfo


class TestDocumentationGenerator:
    """Test the main documentation generator."""
    
    def setup_method(self):
        """Setup for each test."""
        self.generator = DocumentationGenerator(use_ai=False)
    
    def test_initialization_without_ai(self):
        """Test initializing generator without AI."""
        gen = DocumentationGenerator(use_ai=False)
        assert gen.use_ai is False
        assert hasattr(gen, 'parser')
        assert hasattr(gen, 'console')
    
    @patch('codedoc.core.AIExampleGenerator')
    def test_initialization_with_ai(self, mock_ai):
        """Test initializing generator with AI."""
        gen = DocumentationGenerator(use_ai=True, openai_api_key="test-key")
        assert gen.use_ai is True
        mock_ai.assert_called_once_with(api_key="test-key")
    
    def test_generate_documentation_simple_file(self):
        """Test generating documentation for a simple Python file."""
        code = '''
def hello_world():
    """Say hello to the world."""
    return "Hello, World!"

class Greeter:
    """A simple greeter class."""
    
    def greet(self, name: str) -> str:
        """Greet someone by name."""
        return f"Hello, {name}!"
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                result = self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir,
                    format_type="html"
                )
                
                assert result['status'] == 'success'
                assert result['functions_documented'] == 1
                assert result['classes_documented'] == 1
                assert result['ai_enhanced'] is False
                
                # Check output files exist
                output_path = Path(output_dir)
                assert (output_path / 'documentation.html').exists()
                assert (output_path / 'style.css').exists()
                assert (output_path / 'documentation_data.json').exists()
                
            finally:
                Path(temp_file).unlink()
    
    def test_generate_documentation_markdown_format(self):
        """Test generating markdown documentation."""
        code = '''
def simple_function():
    """A simple function."""
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                result = self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir,
                    format_type="markdown"
                )
                
                assert result['status'] == 'success'
                
                # Check markdown file exists
                output_path = Path(output_dir)
                assert (output_path / 'documentation.md').exists()
                assert not (output_path / 'documentation.html').exists()
                
            finally:
                Path(temp_file).unlink()
    
    def test_generate_documentation_both_formats(self):
        """Test generating both HTML and Markdown."""
        code = '''
def test_function():
    """Test function."""
    return True
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                result = self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir,
                    format_type="both"
                )
                
                assert result['status'] == 'success'
                
                # Check both files exist
                output_path = Path(output_dir)
                assert (output_path / 'documentation.html').exists()
                assert (output_path / 'documentation.md').exists()
                assert (output_path / 'style.css').exists()
                
            finally:
                Path(temp_file).unlink()
    
    def test_generate_documentation_empty_file(self):
        """Test handling empty Python file."""
        code = "# Empty file\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                result = self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir
                )
                
                assert result['status'] == 'error'
                assert 'No code elements found' in result['message']
                
            finally:
                Path(temp_file).unlink()
    
    def test_generate_documentation_invalid_file(self):
        """Test handling invalid file types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Not Python code")
            temp_file = f.name
        
        try:
            with pytest.raises(Exception) as exc_info:
                self.generator.generate_documentation(source_path=temp_file)
            
            assert "Unsupported file type" in str(exc_info.value)
            
        finally:
            Path(temp_file).unlink()
    
    def test_generate_documentation_directory(self):
        """Test generating documentation for a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create multiple Python files
            (temp_path / "file1.py").write_text('''
def function1():
    """Function in file1."""
    pass
''')
            
            (temp_path / "file2.py").write_text('''
class Class2:
    """Class in file2."""
    def method(self):
        """A method."""
        pass
''')
            
            with tempfile.TemporaryDirectory() as output_dir:
                result = self.generator.generate_documentation(
                    source_path=temp_dir,
                    output_path=output_dir
                )
                
                assert result['status'] == 'success'
                assert result['functions_documented'] >= 1
                assert result['classes_documented'] >= 1
    
    def test_json_output_format(self):
        """Test JSON output contains correct structure."""
        code = '''
def sample_function(x: int) -> str:
    """Sample function with type hints."""
    return str(x)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir
                )
                
                # Load and check JSON output
                json_file = Path(output_dir) / 'documentation_data.json'
                assert json_file.exists()
                
                with open(json_file) as f:
                    data = json.load(f)
                
                assert 'metadata' in data
                assert 'summary' in data
                assert 'functions' in data
                assert 'classes' in data
                
                assert data['metadata']['generator'] == 'CodeDoc AI'
                assert data['summary']['total_functions'] == 1
                assert len(data['functions']) == 1
                
                func_data = data['functions'][0]
                assert func_data['name'] == 'sample_function'
                assert func_data['args'] == ['x']
                assert func_data['return_annotation'] == 'str'
                
            finally:
                Path(temp_file).unlink()
    
    def test_html_output_content(self):
        """Test HTML output contains expected content."""
        code = '''
def test_html_function():
    """Function for testing HTML output."""
    return "test"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir,
                    format_type="html"
                )
                
                # Check HTML content
                html_file = Path(output_dir) / 'documentation.html'
                html_content = html_file.read_text()
                
                assert '🚀 CodeDoc AI Documentation' in html_content
                assert 'test_html_function' in html_content
                assert 'Function for testing HTML output' in html_content
                assert 'style.css' in html_content
                
            finally:
                Path(temp_file).unlink()
    
    def test_markdown_output_content(self):
        """Test Markdown output contains expected content."""
        code = '''
class TestMarkdownClass:
    """Class for testing Markdown output."""
    
    def test_method(self):
        """Test method."""
        pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        with tempfile.TemporaryDirectory() as output_dir:
            try:
                self.generator.generate_documentation(
                    source_path=temp_file,
                    output_path=output_dir,
                    format_type="markdown"
                )
                
                # Check Markdown content
                md_file = Path(output_dir) / 'documentation.md'
                md_content = md_file.read_text()
                
                assert '# 🚀 CodeDoc AI Documentation' in md_content
                assert '## 🏗️ Classes' in md_content
                assert '### TestMarkdownClass' in md_content
                assert 'Class for testing Markdown output' in md_content
                assert '**🔧 Methods:**' in md_content
                assert 'test_method' in md_content
                
            finally:
                Path(temp_file).unlink()


class TestOutputGeneration:
    """Test specific output generation functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.generator = DocumentationGenerator(use_ai=False)
    
    def test_css_generation(self):
        """Test CSS file generation."""
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = Path(output_dir)
            
            self.generator._generate_css(output_path / 'test.css')
            
            css_file = output_path / 'test.css'
            assert css_file.exists()
            
            css_content = css_file.read_text()
            assert 'CodeDoc AI Styles' in css_content
            assert 'body {' in css_content
            assert 'background: linear-gradient' in css_content 