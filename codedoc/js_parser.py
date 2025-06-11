"""
JavaScript/TypeScript Parser for CodeDoc AI

This module handles parsing JavaScript and TypeScript files to extract:
- Functions and arrow functions
- Classes and methods
- JSDoc comments
- TypeScript type annotations
- ES6 modules and exports
"""

import json
import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class JSFunctionInfo:
    """Information about a JavaScript/TypeScript function."""
    name: str
    params: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    is_async: bool
    is_arrow_function: bool
    is_exported: bool
    line_number: int
    source_code: str
    jsdoc_tags: Dict[str, Any]


@dataclass
class JSClassInfo:
    """Information about a JavaScript/TypeScript class."""
    name: str
    methods: List[JSFunctionInfo]
    properties: List[str]
    docstring: Optional[str]
    extends: Optional[str]
    is_exported: bool
    line_number: int
    source_code: str
    jsdoc_tags: Dict[str, Any]


@dataclass
class JSFileInfo:
    """Information about a JavaScript/TypeScript file."""
    file_path: str
    functions: List[JSFunctionInfo]
    classes: List[JSClassInfo]
    imports: List[str]
    exports: List[str]


class JavaScriptParser:
    """Parser for JavaScript and TypeScript files using Babel."""
    
    def __init__(self):
        """Initialize the JavaScript parser."""
        self.ensure_babel_installed()
    
    def ensure_babel_installed(self) -> None:
        """Ensure Babel parser is available."""
        try:
            # Check if we can import babel parser from Node.js
            subprocess.run(
                ["node", "-e", "require('@babel/parser')"],
                check=True,
                capture_output=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Babel parser not found. Installing...")
            self._install_babel()
    
    def _install_babel(self) -> None:
        """Install Babel parser via npm."""
        try:
            subprocess.run(
                ["npm", "install", "@babel/parser", "@babel/traverse"],
                check=True,
                capture_output=True
            )
            print("✅ Babel parser installed successfully!")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "Failed to install Babel parser. Please install Node.js and npm first."
            ) from e
    
    def parse_file(self, file_path: str) -> JSFileInfo:
        """Parse a JavaScript/TypeScript file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content, file_path)
    
    def parse_content(self, content: str, file_path: str = "<string>") -> JSFileInfo:
        """Parse JavaScript/TypeScript content."""
        ast_data = self._parse_to_ast(content, file_path)
        return self._extract_info_from_ast(ast_data, content, file_path)
    
    def _parse_to_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """Parse content to AST using Babel."""
        # Create temporary file for parsing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Create Node.js script to parse with Babel
            parser_script = f'''
const parser = require('@babel/parser');
const fs = require('fs');

const code = fs.readFileSync('{tmp_path}', 'utf8');

const ast = parser.parse(code, {{
    sourceType: 'module',
    allowImportExportEverywhere: true,
    allowReturnOutsideFunction: true,
    plugins: [
        'jsx',
        'typescript',
        'decorators-legacy',
        'classProperties',
        'asyncGenerators',
        'functionBind',
        'exportDefaultFrom',
        'exportNamespaceFrom',
        'dynamicImport',
        'nullishCoalescingOperator',
        'optionalChaining'
    ]
}});

console.log(JSON.stringify(ast, null, 2));
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as script_tmp:
                script_tmp.write(parser_script)
                script_path = script_tmp.name
            
            try:
                result = subprocess.run(
                    ["node", script_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return json.loads(result.stdout)
            finally:
                os.unlink(script_path)
        
        finally:
            os.unlink(tmp_path)
    
    def _extract_info_from_ast(self, ast: Dict[str, Any], content: str, file_path: str) -> JSFileInfo:
        """Extract information from AST."""
        lines = content.split('\n')
        
        functions = []
        classes = []
        imports = []
        exports = []
        
        # Walk through AST body
        for node in ast.get('body', []):
            if node['type'] == 'FunctionDeclaration':
                func_info = self._extract_function_info(node, lines)
                if func_info:
                    functions.append(func_info)
            
            elif node['type'] == 'ClassDeclaration':
                class_info = self._extract_class_info(node, lines)
                if class_info:
                    classes.append(class_info)
            
            elif node['type'] == 'ImportDeclaration':
                imports.append(self._extract_import_info(node))
            
            elif node['type'] == 'ExportNamedDeclaration':
                export_info = self._extract_export_info(node)
                if export_info:
                    exports.append(export_info)
            
            elif node['type'] == 'VariableDeclaration':
                # Check for arrow functions
                for declarator in node.get('declarations', []):
                    if declarator.get('init', {}).get('type') == 'ArrowFunctionExpression':
                        func_info = self._extract_arrow_function_info(declarator, lines)
                        if func_info:
                            functions.append(func_info)
        
        return JSFileInfo(
            file_path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            exports=exports
        )
    
    def _extract_function_info(self, node: Dict[str, Any], lines: List[str]) -> Optional[JSFunctionInfo]:
        """Extract function information from AST node."""
        try:
            name = node.get('id', {}).get('name', 'anonymous')
            line_number = node.get('loc', {}).get('start', {}).get('line', 1)
            
            # Extract parameters
            params = []
            for param in node.get('params', []):
                if param['type'] == 'Identifier':
                    params.append(param['name'])
                elif param['type'] == 'AssignmentPattern':
                    # Default parameters
                    params.append(f"{param['left']['name']}={self._get_source_text(param['right'])}")
            
            # Extract JSDoc
            docstring, jsdoc_tags = self._extract_jsdoc(node, lines, line_number)
            
            # Get return type from JSDoc or TypeScript annotations
            return_type = jsdoc_tags.get('returns', {}).get('type') if jsdoc_tags else None
            
            # Extract source code
            start_line = line_number - 1
            end_line = node.get('loc', {}).get('end', {}).get('line', start_line + 1)
            source_code = '\n'.join(lines[start_line:end_line])
            
            return JSFunctionInfo(
                name=name,
                params=params,
                return_type=return_type,
                docstring=docstring,
                is_async=node.get('async', False),
                is_arrow_function=False,
                is_exported=False,  # Will be updated if part of export
                line_number=line_number,
                source_code=source_code,
                jsdoc_tags=jsdoc_tags
            )
        
        except Exception:
            return None
    
    def _extract_arrow_function_info(self, node: Dict[str, Any], lines: List[str]) -> Optional[JSFunctionInfo]:
        """Extract arrow function information."""
        try:
            name = node.get('id', {}).get('name', 'anonymous')
            arrow_func = node.get('init', {})
            line_number = node.get('loc', {}).get('start', {}).get('line', 1)
            
            # Extract parameters
            params = []
            for param in arrow_func.get('params', []):
                if param['type'] == 'Identifier':
                    params.append(param['name'])
            
            # Extract JSDoc
            docstring, jsdoc_tags = self._extract_jsdoc(node, lines, line_number)
            
            # Extract source code
            start_line = line_number - 1
            end_line = arrow_func.get('loc', {}).get('end', {}).get('line', start_line + 1)
            source_code = '\n'.join(lines[start_line:end_line])
            
            return JSFunctionInfo(
                name=name,
                params=params,
                return_type=None,
                docstring=docstring,
                is_async=arrow_func.get('async', False),
                is_arrow_function=True,
                is_exported=False,
                line_number=line_number,
                source_code=source_code,
                jsdoc_tags=jsdoc_tags
            )
        
        except Exception:
            return None
    
    def _extract_class_info(self, node: Dict[str, Any], lines: List[str]) -> Optional[JSClassInfo]:
        """Extract class information from AST node."""
        try:
            name = node.get('id', {}).get('name', 'Anonymous')
            line_number = node.get('loc', {}).get('start', {}).get('line', 1)
            
            # Extract methods
            methods = []
            properties = []
            
            for member in node.get('body', {}).get('body', []):
                if member['type'] == 'MethodDefinition':
                    method_info = self._extract_method_info(member, lines)
                    if method_info:
                        methods.append(method_info)
                elif member['type'] == 'PropertyDefinition':
                    prop_name = member.get('key', {}).get('name')
                    if prop_name:
                        properties.append(prop_name)
            
            # Extract JSDoc
            docstring, jsdoc_tags = self._extract_jsdoc(node, lines, line_number)
            
            # Check for extends
            extends = None
            if node.get('superClass'):
                extends = node['superClass'].get('name')
            
            # Extract source code
            start_line = line_number - 1
            end_line = node.get('loc', {}).get('end', {}).get('line', start_line + 1)
            source_code = '\n'.join(lines[start_line:end_line])
            
            return JSClassInfo(
                name=name,
                methods=methods,
                properties=properties,
                docstring=docstring,
                extends=extends,
                is_exported=False,
                line_number=line_number,
                source_code=source_code,
                jsdoc_tags=jsdoc_tags
            )
        
        except Exception:
            return None
    
    def _extract_method_info(self, node: Dict[str, Any], lines: List[str]) -> Optional[JSFunctionInfo]:
        """Extract method information from class."""
        try:
            name = node.get('key', {}).get('name', 'anonymous')
            func_node = node.get('value', {})
            line_number = node.get('loc', {}).get('start', {}).get('line', 1)
            
            # Extract parameters
            params = []
            for param in func_node.get('params', []):
                if param['type'] == 'Identifier':
                    params.append(param['name'])
            
            # Extract JSDoc
            docstring, jsdoc_tags = self._extract_jsdoc(node, lines, line_number)
            
            # Extract source code
            start_line = line_number - 1
            end_line = node.get('loc', {}).get('end', {}).get('line', start_line + 1)
            source_code = '\n'.join(lines[start_line:end_line])
            
            return JSFunctionInfo(
                name=name,
                params=params,
                return_type=None,
                docstring=docstring,
                is_async=func_node.get('async', False),
                is_arrow_function=False,
                is_exported=False,
                line_number=line_number,
                source_code=source_code,
                jsdoc_tags=jsdoc_tags
            )
        
        except Exception:
            return None
    
    def _extract_jsdoc(self, node: Dict[str, Any], lines: List[str], line_number: int) -> tuple[Optional[str], Dict[str, Any]]:
        """Extract JSDoc comment and parse tags."""
        # Look for JSDoc comment before the node
        jsdoc_tags = {}
        docstring = None
        
        # Check a few lines before the current line for JSDoc comments
        for i in range(max(0, line_number - 10), line_number):
            line = lines[i].strip()
            if line.startswith('/**'):
                # Found JSDoc start, extract the full comment
                jsdoc_lines = []
                j = i
                while j < len(lines) and not lines[j].strip().endswith('*/'):
                    jsdoc_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    jsdoc_lines.append(lines[j])
                
                # Parse JSDoc
                jsdoc_content = '\n'.join(jsdoc_lines)
                docstring, jsdoc_tags = self._parse_jsdoc(jsdoc_content)
                break
        
        return docstring, jsdoc_tags
    
    def _parse_jsdoc(self, jsdoc_content: str) -> tuple[Optional[str], Dict[str, Any]]:
        """Parse JSDoc content to extract description and tags."""
        lines = jsdoc_content.split('\n')
        description_lines = []
        tags = {}
        
        current_tag = None
        current_tag_content = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('/**') or line.startswith('*/'):
                continue
            if line.startswith('*'):
                line = line[1:].strip()
            
            if line.startswith('@'):
                # Save previous tag
                if current_tag:
                    tags[current_tag] = ' '.join(current_tag_content)
                
                # Parse new tag
                parts = line[1:].split(None, 1)
                current_tag = parts[0]
                current_tag_content = [parts[1]] if len(parts) > 1 else []
            elif current_tag:
                current_tag_content.append(line)
            else:
                description_lines.append(line)
        
        # Save last tag
        if current_tag:
            tags[current_tag] = ' '.join(current_tag_content)
        
        description = ' '.join(description_lines).strip() if description_lines else None
        return description, tags
    
    def _extract_import_info(self, node: Dict[str, Any]) -> str:
        """Extract import information."""
        source = node.get('source', {}).get('value', '')
        specifiers = []
        
        for spec in node.get('specifiers', []):
            if spec['type'] == 'ImportDefaultSpecifier':
                specifiers.append(spec['local']['name'])
            elif spec['type'] == 'ImportSpecifier':
                specifiers.append(spec['local']['name'])
        
        if specifiers:
            return f"import {{{', '.join(specifiers)}}} from '{source}'"
        return f"import '{source}'"
    
    def _extract_export_info(self, node: Dict[str, Any]) -> Optional[str]:
        """Extract export information."""
        if node.get('declaration'):
            decl = node['declaration']
            if decl['type'] == 'FunctionDeclaration':
                return decl.get('id', {}).get('name')
            elif decl['type'] == 'ClassDeclaration':
                return decl.get('id', {}).get('name')
        return None
    
    def _get_source_text(self, node: Dict[str, Any]) -> str:
        """Get source text representation of a node."""
        if node['type'] == 'Literal':
            return str(node.get('value', ''))
        elif node['type'] == 'Identifier':
            return node.get('name', '')
        return 'unknown' 