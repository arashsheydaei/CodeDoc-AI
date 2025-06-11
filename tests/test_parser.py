"""
Tests for CodeParser Module 🔍

Testing Python code parsing functionality.
"""

import pytest
import tempfile
from pathlib import Path

from codedoc.parser import CodeParser, FunctionInfo, ClassInfo


class TestCodeParser:
    """Test the Python code parser."""
    
    def setup_method(self):
        """Setup for each test."""
        self.parser = CodeParser()
    
    def test_simple_function_parsing(self):
        """Test parsing a simple function."""
        code = '''
def hello_world():
    """Say hello to the world."""
    return "Hello, World!"
'''
        result = self.parser.parse_code(code)
        
        assert len(result['functions']) == 1
        assert len(result['classes']) == 0
        
        func = result['functions'][0]
        assert func.name == 'hello_world'
        assert func.docstring == 'Say hello to the world.'
        assert func.args == []
    
    def test_function_with_parameters(self):
        """Test parsing function with parameters and type hints."""
        code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b
'''
        result = self.parser.parse_code(code)
        
        func = result['functions'][0]
        assert func.name == 'calculate_sum'
        assert func.args == ['a', 'b']
        assert func.arg_annotations == {'a': 'int', 'b': 'int'}
        assert func.return_annotation == 'int'
        assert func.docstring == 'Calculate sum of two numbers.'
    
    def test_class_parsing(self):
        """Test parsing a simple class."""
        code = '''
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize calculator."""
        self.value = 0
    
    def add(self, x: float) -> float:
        """Add a number."""
        self.value += x
        return self.value
'''
        result = self.parser.parse_code(code)
        
        assert len(result['classes']) == 1
        assert len(result['functions']) == 0
        
        cls = result['classes'][0]
        assert cls.name == 'Calculator'
        assert cls.docstring == 'A simple calculator class.'
        assert len(cls.methods) == 2
        
        # Check methods
        method_names = [m.name for m in cls.methods]
        assert '__init__' in method_names
        assert 'add' in method_names
    
    def test_complex_code_parsing(self):
        """Test parsing code with both functions and classes."""
        code = '''
"""Module docstring."""

import math
from typing import List

def utility_function(data: List[str]) -> int:
    """A utility function."""
    return len(data)

class DataProcessor:
    """Process data efficiently."""
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, items: List[str]) -> List[str]:
        """Process items."""
        return [item.upper() for item in items]

def another_function():
    """Another function without parameters."""
    pass
'''
        result = self.parser.parse_code(code)
        
        assert len(result['functions']) == 2
        assert len(result['classes']) == 1
        assert result['total_items'] == 3
        
        # Check function names
        func_names = [f.name for f in result['functions']]
        assert 'utility_function' in func_names
        assert 'another_function' in func_names
        
        # Check class
        cls = result['classes'][0]
        assert cls.name == 'DataProcessor'
        assert len(cls.methods) == 2
    
    def test_file_parsing(self):
        """Test parsing from a file."""
        code = '''
def test_function():
    """Test function."""
    return True
'''
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = self.parser.parse_file(temp_path)
            assert len(result['functions']) == 1
            assert result['functions'][0].name == 'test_function'
        finally:
            Path(temp_path).unlink()
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        invalid_code = '''
def invalid_function(
    # Missing closing parenthesis and colon
    return "This won't parse"
'''
        
        with pytest.raises(Exception) as exc_info:
            self.parser.parse_code(invalid_code)
        
        assert "Syntax error" in str(exc_info.value)
    
    def test_empty_code(self):
        """Test parsing empty or whitespace-only code."""
        result = self.parser.parse_code("   \n   \n   ")
        
        assert len(result['functions']) == 0
        assert len(result['classes']) == 0
        assert result['total_items'] == 0
    
    def test_function_with_complex_annotations(self):
        """Test parsing functions with complex type annotations."""
        code = '''
from typing import Dict, List, Optional, Union

def complex_function(
    data: Dict[str, List[int]], 
    options: Optional[Union[str, int]] = None
) -> Dict[str, Union[int, str]]:
    """Function with complex type annotations."""
    return {}
'''
        result = self.parser.parse_code(code)
        
        func = result['functions'][0]
        assert func.name == 'complex_function'
        assert 'data' in func.arg_annotations
        assert 'options' in func.arg_annotations
        assert func.return_annotation is not None
    
    def test_class_inheritance(self):
        """Test parsing class with inheritance."""
        code = '''
class BaseClass:
    """Base class."""
    pass

class DerivedClass(BaseClass):
    """Derived class."""
    
    def method(self):
        """A method."""
        pass
'''
        result = self.parser.parse_code(code)
        
        assert len(result['classes']) == 2
        
        # Check derived class
        derived = [c for c in result['classes'] if c.name == 'DerivedClass'][0]
        assert 'BaseClass' in derived.bases
    
    def test_parser_summary(self):
        """Test parser summary functionality."""
        code = '''
def func1(): pass
def func2(): pass

class Class1: pass
'''
        result = self.parser.parse_code(code)
        summary = self.parser.get_summary()
        
        assert "2 functions" in summary
        assert "1 classes" in summary


class TestFunctionInfo:
    """Test FunctionInfo dataclass."""
    
    def test_function_info_creation(self):
        """Test creating FunctionInfo objects."""
        func_info = FunctionInfo(
            name="test_func",
            args=["a", "b"],
            docstring="Test function",
            source_code="def test_func(a, b): pass",
            line_number=1
        )
        
        assert func_info.name == "test_func"
        assert func_info.args == ["a", "b"]
        assert func_info.docstring == "Test function"
        assert func_info.arg_annotations == {}  # Default empty dict
    
    def test_function_info_with_annotations(self):
        """Test FunctionInfo with type annotations."""
        func_info = FunctionInfo(
            name="typed_func",
            args=["x", "y"],
            docstring="Typed function",
            source_code="def typed_func(x: int, y: str) -> bool: pass",
            line_number=5,
            return_annotation="bool",
            arg_annotations={"x": "int", "y": "str"}
        )
        
        assert func_info.return_annotation == "bool"
        assert func_info.arg_annotations["x"] == "int"
        assert func_info.arg_annotations["y"] == "str"


class TestClassInfo:
    """Test ClassInfo dataclass."""
    
    def test_class_info_creation(self):
        """Test creating ClassInfo objects."""
        method = FunctionInfo(
            name="method1",
            args=["self"],
            docstring="A method",
            source_code="def method1(self): pass",
            line_number=3
        )
        
        class_info = ClassInfo(
            name="TestClass",
            docstring="Test class",
            methods=[method],
            source_code="class TestClass: pass",
            line_number=1
        )
        
        assert class_info.name == "TestClass"
        assert class_info.docstring == "Test class"
        assert len(class_info.methods) == 1
        assert class_info.methods[0].name == "method1"
        assert class_info.bases == []  # Default empty list
    
    def test_class_info_with_inheritance(self):
        """Test ClassInfo with base classes."""
        class_info = ClassInfo(
            name="DerivedClass",
            docstring="Derived class",
            methods=[],
            source_code="class DerivedClass(BaseClass): pass",
            line_number=1,
            bases=["BaseClass"]
        )
        
        assert class_info.bases == ["BaseClass"] 