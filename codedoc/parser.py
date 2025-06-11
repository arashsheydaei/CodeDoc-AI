"""
Code Parser Module 🔍

Parses Python code and extracts functions, classes, and documentation.
"""

import ast
import inspect
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import astunparse


@dataclass
class FunctionInfo:
    """Information about a parsed function."""
    name: str
    args: List[str]
    docstring: Optional[str]
    source_code: str
    line_number: int
    return_annotation: Optional[str] = None
    arg_annotations: Dict[str, str] = None
    
    def __post_init__(self):
        if self.arg_annotations is None:
            self.arg_annotations = {}


@dataclass
class ClassInfo:
    """Information about a parsed class."""
    name: str
    docstring: Optional[str]
    methods: List[FunctionInfo]
    source_code: str
    line_number: int
    bases: List[str] = None
    
    def __post_init__(self):
        if self.bases is None:
            self.bases = []


class CodeParser:
    """🔍 Smart Python Code Parser using AST."""
    
    def __init__(self):
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Python file and extract all functions and classes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            return self.parse_code(source_code)
        except Exception as e:
            raise Exception(f"❌ Error parsing file {file_path}: {str(e)}")
    
    def parse_code(self, source_code: str) -> Dict[str, Any]:
        """Parse Python source code and extract documentation info."""
        try:
            tree = ast.parse(source_code)
            self.functions = []
            self.classes = []
            
            # First pass: collect all classes and their methods
            class_methods = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_methods.add(id(item))
            
            # Second pass: collect top-level functions and classes
            for node in tree.body:  # Only look at top-level nodes
                if isinstance(node, ast.FunctionDef):
                    self._parse_function(node, source_code)
                elif isinstance(node, ast.ClassDef):
                    self._parse_class(node, source_code)
            
            return {
                'functions': self.functions,
                'classes': self.classes,
                'total_items': len(self.functions) + len(self.classes)
            }
        
        except SyntaxError as e:
            raise Exception(f"❌ Syntax error in code: {str(e)}")
        except Exception as e:
            raise Exception(f"❌ Error parsing code: {str(e)}")
    
    def _parse_function(self, node: ast.FunctionDef, source_code: str) -> None:
        """Parse a function node and extract information."""
        # Get function arguments
        args = []
        arg_annotations = {}
        
        for arg in node.args.args:
            args.append(arg.arg)
            if arg.annotation:
                arg_annotations[arg.arg] = astunparse.unparse(arg.annotation).strip()
        
        # Get return annotation
        return_annotation = None
        if node.returns:
            return_annotation = astunparse.unparse(node.returns).strip()
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get source code for this function
        func_source = astunparse.unparse(node)
        
        function_info = FunctionInfo(
            name=node.name,
            args=args,
            docstring=docstring,
            source_code=func_source,
            line_number=node.lineno,
            return_annotation=return_annotation,
            arg_annotations=arg_annotations
        )
        
        self.functions.append(function_info)
    
    def _parse_class(self, node: ast.ClassDef, source_code: str) -> None:
        """Parse a class node and extract information."""
        # Get class bases
        bases = []
        for base in node.bases:
            bases.append(astunparse.unparse(base).strip())
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Parse method
                method_args = []
                method_arg_annotations = {}
                
                for arg in item.args.args:
                    method_args.append(arg.arg)
                    if arg.annotation:
                        method_arg_annotations[arg.arg] = astunparse.unparse(arg.annotation).strip()
                
                method_return_annotation = None
                if item.returns:
                    method_return_annotation = astunparse.unparse(item.returns).strip()
                
                method_docstring = ast.get_docstring(item)
                method_source = astunparse.unparse(item)
                
                method_info = FunctionInfo(
                    name=item.name,
                    args=method_args,
                    docstring=method_docstring,
                    source_code=method_source,
                    line_number=item.lineno,
                    return_annotation=method_return_annotation,
                    arg_annotations=method_arg_annotations
                )
                methods.append(method_info)
        
        # Get source code for this class
        class_source = astunparse.unparse(node)
        
        class_info = ClassInfo(
            name=node.name,
            docstring=docstring,
            methods=methods,
            source_code=class_source,
            line_number=node.lineno,
            bases=bases
        )
        
        self.classes.append(class_info)
    
    def get_summary(self) -> str:
        """Get a summary of parsed code."""
        return f"📊 Found {len(self.functions)} functions and {len(self.classes)} classes" 