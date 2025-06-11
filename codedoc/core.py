"""
Core Documentation Generator Module 🚀

Main orchestrator that combines parsing, AI generation, and output formatting.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from jinja2 import Template
from rich.console import Console
from rich.progress import track
from dataclasses import asdict

from .parser import CodeParser
from .js_parser import JavaScriptParser, JSFileInfo
from .ai import AIExampleGenerator
from .templates import HTMLTemplate, MarkdownTemplate


class DocumentationGenerator:
    """🚀 Main Documentation Generator - The heart of CodeDoc AI."""
    
    def __init__(self, use_ai: bool = True, ai_provider: str = "openai"):
        """Initialize the documentation generator.
        
        Args:
            use_ai: Whether to use AI for enhancing documentation
            ai_provider: AI provider to use ('openai', 'anthropic', etc.)
        """
        self.console = Console()
        self.use_ai = use_ai
        self.python_parser = CodeParser()
        self.js_parser = JavaScriptParser()
        try:
            self.ai_enhancer = AIExampleGenerator() if use_ai else None
        except Exception:
            self.ai_enhancer = None
            self.use_ai = False
        self.html_template = HTMLTemplate()
        self.markdown_template = MarkdownTemplate()
        
        if use_ai:
            try:
                self.console.print("🤖 AI Generator initialized!", style="green")
            except Exception as e:
                self.console.print(f"⚠️  AI Generator failed to initialize: {str(e)}", style="yellow")
                self.console.print("📝 Continuing without AI features...", style="yellow")
                self.use_ai = False
        
        self.generated_docs: Dict[str, Any] = {}
    
    def generate_documentation(
        self, 
        source_path: str, 
        output_format: str = "html",
        output_path: Optional[str] = None,
        include_private: bool = False,
        language: Optional[str] = None
    ) -> str:
        """Generate documentation for source code.
        
        Args:
            source_path: Path to source file or directory
            output_format: Output format ('html', 'markdown', 'json')
            output_path: Optional output path
            include_private: Whether to include private methods/functions
            language: Force specific language ('python', 'javascript', 'typescript')
            
        Returns:
            Generated documentation as string
        """
        # Determine if it's a file or directory
        path = Path(source_path)
        if path.is_file():
            return self._generate_file_documentation(
                source_path, output_format, output_path, include_private, language
            )
        elif path.is_dir():
            return self._generate_directory_documentation(
                source_path, output_format, output_path, include_private, language
            )
        else:
            raise ValueError(f"Invalid source path: {source_path}")
    
    def _generate_file_documentation(
        self, 
        file_path: str, 
        output_format: str,
        output_path: Optional[str],
        include_private: bool,
        language: Optional[str]
    ) -> str:
        """Generate documentation for a single file."""
        # Detect language if not specified
        if not language:
            language = self._detect_language(file_path)
        
        # Parse the file based on language
        if language == "python":
            python_result = self.python_parser.parse_file(file_path)
            parsed_data = self._prepare_python_data(python_result, file_path, include_private)
        elif language in ["javascript", "typescript"]:
            js_file_info = self.js_parser.parse_file(file_path)
            parsed_data = self._prepare_javascript_data(js_file_info, include_private)
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        # Enhance with AI if enabled
        if self.use_ai and self.ai_enhancer:
            enhanced_data = self._enhance_with_ai(parsed_data, language)
        else:
            enhanced_data = parsed_data
        
        # Generate output
        if output_format == "html":
            content = self.html_template.render(enhanced_data)
        elif output_format == "markdown":
            content = self.markdown_template.render(enhanced_data)
        elif output_format == "json":
            import json
            content = json.dumps(enhanced_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Save to file if output path specified
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def _generate_directory_documentation(
        self, 
        dir_path: str, 
        output_format: str,
        output_path: Optional[str],
        include_private: bool,
        language: Optional[str]
    ) -> str:
        """Generate documentation for all files in a directory."""
        path = Path(dir_path)
        all_files_data = []
        
        # Find all supported source files
        if language == "python":
            pattern = "**/*.py"
        elif language == "javascript":
            pattern = "**/*.js"
        elif language == "typescript":
            pattern = "**/*.ts"
        else:
            # Auto-detect: include all supported extensions
            python_files = list(path.glob("**/*.py"))
            js_files = list(path.glob("**/*.js"))
            ts_files = list(path.glob("**/*.ts"))
            all_source_files = python_files + js_files + ts_files
        
        if language:
            source_files = list(path.glob(pattern))
        else:
            source_files = all_source_files
        
        for file_path in source_files:
            try:
                # Skip __pycache__ and similar directories
                if any(part.startswith('.') or part == '__pycache__' for part in file_path.parts):
                    continue
                
                file_lang = language or self._detect_language(str(file_path))
                
                # Parse based on detected language
                if file_lang == "python":
                    python_result = self.python_parser.parse_file(str(file_path))
                    file_data = self._prepare_python_data(python_result, str(file_path), include_private)
                elif file_lang in ["javascript", "typescript"]:
                    js_file_info = self.js_parser.parse_file(str(file_path))
                    file_data = self._prepare_javascript_data(js_file_info, include_private)
                else:
                    continue  # Skip unsupported files
                
                # Enhance with AI if enabled
                if self.use_ai and self.ai_enhancer:
                    file_data = self._enhance_with_ai(file_data, file_lang)
                
                all_files_data.append(file_data)
                
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}")
                continue
        
        # Combine all file data
        combined_data = {
            "project_name": path.name,
            "files": all_files_data,
            "total_files": len(all_files_data),
            "languages": list(set(file_data.get("language", "unknown") for file_data in all_files_data))
        }
        
        # Generate output
        if output_format == "html":
            content = self.html_template.render_project(combined_data)
        elif output_format == "markdown":
            content = self.markdown_template.render_project(combined_data)
        elif output_format == "json":
            import json
            content = json.dumps(combined_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        # Save to file if output path specified
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return content
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        extension = Path(file_path).suffix.lower()
        
        if extension == ".py":
            return "python"
        elif extension == ".js":
            return "javascript"
        elif extension == ".ts":
            return "typescript"
        elif extension == ".jsx":
            return "javascript"
        elif extension == ".tsx":
            return "typescript"
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
    
    def _prepare_python_data(self, python_result: Dict[str, Any], file_path: str, include_private: bool) -> Dict[str, Any]:
        """Prepare Python file data for documentation generation."""
        # Filter private items if requested
        functions = python_result['functions']
        classes = python_result['classes']
        
        if not include_private:
            functions = [f for f in functions if not f.name.startswith('_')]
            classes = [c for c in classes if not c.name.startswith('_')]
            # Also filter private methods from classes
            for cls in classes:
                cls.methods = [m for m in cls.methods if not m.name.startswith('_')]
        
        return {
            "language": "python",
            "file_path": file_path,
            "functions": [asdict(f) for f in functions],
            "classes": [asdict(c) for c in classes],
            "imports": [],  # CodeParser doesn't extract imports yet
            "total_functions": len(functions),
            "total_classes": len(classes)
        }
    
    def _prepare_javascript_data(self, js_file_info: JSFileInfo, include_private: bool) -> Dict[str, Any]:
        """Prepare JavaScript/TypeScript file data for documentation generation."""
        # Filter private items if requested (items starting with _)
        functions = js_file_info.functions
        classes = js_file_info.classes
        
        if not include_private:
            functions = [f for f in functions if not f.name.startswith('_')]
            classes = [c for c in classes if not c.name.startswith('_')]
            # Also filter private methods from classes
            for cls in classes:
                cls.methods = [m for m in cls.methods if not m.name.startswith('_')]
        
        # Detect if it's TypeScript based on file extension
        language = "typescript" if js_file_info.file_path.endswith(('.ts', '.tsx')) else "javascript"
        
        return {
            "language": language,
            "file_path": js_file_info.file_path,
            "functions": [asdict(f) for f in functions],
            "classes": [asdict(c) for c in classes],
            "imports": js_file_info.imports,
            "exports": js_file_info.exports,
            "total_functions": len(functions),
            "total_classes": len(classes)
        }
    
    def _enhance_with_ai(self, data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Enhance documentation data with AI-generated content."""
        enhanced_data = data.copy()
        
        # Enhance functions
        enhanced_functions = []
        for func_data in data.get("functions", []):
            try:
                if language == "python":
                    enhanced_func = self.ai_enhancer.enhance_function_documentation(
                        func_data["name"],
                        func_data["params"],
                        func_data.get("docstring"),
                        func_data["source_code"],
                        language="python",
                        return_type=func_data.get("return_type")
                    )
                else:  # JavaScript/TypeScript
                    enhanced_func = self.ai_enhancer.enhance_function_documentation(
                        func_data["name"],
                        func_data["params"],
                        func_data.get("docstring"),
                        func_data["source_code"],
                        language=language,
                        return_type=func_data.get("return_type"),
                        is_async=func_data.get("is_async", False)
                    )
                
                # Merge with original data
                func_data.update(enhanced_func)
                enhanced_functions.append(func_data)
                
            except Exception as e:
                print(f"Warning: Failed to enhance function {func_data['name']}: {e}")
                enhanced_functions.append(func_data)
        
        enhanced_data["functions"] = enhanced_functions
        
        # Enhance classes
        enhanced_classes = []
        for class_data in data.get("classes", []):
            try:
                enhanced_class = self.ai_enhancer.enhance_class_documentation(
                    class_data["name"],
                    [m["name"] for m in class_data.get("methods", [])],
                    class_data.get("docstring"),
                    class_data["source_code"],
                    language=language
                )
                
                # Merge with original data
                class_data.update(enhanced_class)
                enhanced_classes.append(class_data)
                
            except Exception as e:
                print(f"Warning: Failed to enhance class {class_data['name']}: {e}")
                enhanced_classes.append(class_data)
        
        enhanced_data["classes"] = enhanced_classes
        
        return enhanced_data 