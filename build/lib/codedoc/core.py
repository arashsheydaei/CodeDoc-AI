"""
Core Documentation Generator Module 🚀

Main orchestrator that combines parsing, AI generation, and output formatting.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jinja2 import Template
from rich.console import Console
from rich.progress import track

from .parser import CodeParser, FunctionInfo, ClassInfo
from .ai import AIExampleGenerator


class DocumentationGenerator:
    """🚀 Main Documentation Generator - The heart of CodeDoc AI."""
    
    def __init__(self, openai_api_key: Optional[str] = None, use_ai: bool = True):
        """Initialize the documentation generator."""
        self.console = Console()
        self.parser = CodeParser()
        self.use_ai = use_ai
        
        if use_ai:
            try:
                self.ai_generator = AIExampleGenerator(api_key=openai_api_key)
                self.console.print("🤖 AI Generator initialized!", style="green")
            except Exception as e:
                self.console.print(f"⚠️  AI Generator failed to initialize: {str(e)}", style="yellow")
                self.console.print("📝 Continuing without AI features...", style="yellow")
                self.use_ai = False
        
        self.generated_docs: Dict[str, Any] = {}
    
    def generate_documentation(self, 
                             source_path: str, 
                             output_path: str = "./docs",
                             format_type: str = "html") -> Dict[str, Any]:
        """Generate comprehensive documentation for Python code."""
        
        self.console.print("🚀 Starting CodeDoc AI Documentation Generation...", style="bold blue")
        
        # Step 1: Parse the code
        self.console.print("🔍 Parsing Python code...", style="cyan")
        parsed_data = self._parse_source(source_path)
        
        if parsed_data['total_items'] == 0:
            self.console.print("❌ No functions or classes found to document!", style="red")
            return {"status": "error", "message": "No code elements found"}
        
        self.console.print(f"📊 Found {parsed_data['total_items']} code elements", style="green")
        
        # Step 2: Generate AI-enhanced documentation
        if self.use_ai:
            self.console.print("🤖 Generating AI-powered examples and explanations...", style="cyan")
            enhanced_data = self._enhance_with_ai(parsed_data)
        else:
            # For non-AI mode, wrap the data in the expected format
            enhanced_functions = []
            enhanced_classes = []
            
            for func in parsed_data['functions']:
                enhanced_functions.append({
                    'info': func,
                    'ai_content': {},
                    'enhanced_docstring': func.docstring
                })
            
            for cls in parsed_data['classes']:
                enhanced_classes.append({
                    'info': cls,
                    'ai_content': {},
                    'enhanced_docstring': cls.docstring
                })
            
            enhanced_data = {
                'functions': enhanced_functions,
                'classes': enhanced_classes,
                'total_items': len(enhanced_functions) + len(enhanced_classes)
            }
            self.console.print("📝 Generating basic documentation (no AI)...", style="cyan")
        
        # Step 3: Generate output files
        self.console.print(f"📄 Generating {format_type.upper()} documentation...", style="cyan")
        output_info = self._generate_output(enhanced_data, output_path, format_type)
        
        # Step 4: Create summary
        summary = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "source_path": source_path,
            "output_path": output_path,
            "format": format_type,
            "functions_documented": len(enhanced_data['functions']),
            "classes_documented": len(enhanced_data['classes']),
            "ai_enhanced": self.use_ai,
            "output_files": output_info['files']
        }
        
        self.console.print("✅ Documentation generation completed!", style="bold green")
        self.console.print(f"📁 Output saved to: {output_path}", style="green")
        
        return summary
    
    def _parse_source(self, source_path: str) -> Dict[str, Any]:
        """Parse source code from file or directory."""
        source_path = Path(source_path)
        
        if source_path.is_file():
            if source_path.suffix == '.py':
                return self.parser.parse_file(str(source_path))
            else:
                raise Exception(f"❌ Unsupported file type: {source_path.suffix}")
        
        elif source_path.is_dir():
            # Parse all Python files in directory
            all_functions = []
            all_classes = []
            
            python_files = list(source_path.rglob("*.py"))
            if not python_files:
                raise Exception(f"❌ No Python files found in {source_path}")
            
            for py_file in track(python_files, description="Parsing files..."):
                try:
                    file_data = self.parser.parse_file(str(py_file))
                    all_functions.extend(file_data['functions'])
                    all_classes.extend(file_data['classes'])
                except Exception as e:
                    self.console.print(f"⚠️  Skipping {py_file}: {str(e)}", style="yellow")
            
            return {
                'functions': all_functions,
                'classes': all_classes,
                'total_items': len(all_functions) + len(all_classes)
            }
        
        else:
            raise Exception(f"❌ Source path not found: {source_path}")
    
    def _enhance_with_ai(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance parsed data with AI-generated content."""
        enhanced_functions = []
        enhanced_classes = []
        
        # Enhance functions
        for func in track(parsed_data['functions'], description="AI enhancing functions..."):
            try:
                ai_content = self.ai_generator.generate_function_examples(func)
                enhanced_func = {
                    'info': func,
                    'ai_content': ai_content,
                    'enhanced_docstring': self.ai_generator.enhance_docstring(func.docstring, func.name)
                }
                enhanced_functions.append(enhanced_func)
            except Exception as e:
                self.console.print(f"⚠️  AI enhancement failed for {func.name}: {str(e)}", style="yellow")
                enhanced_functions.append({'info': func, 'ai_content': {}, 'enhanced_docstring': func.docstring})
        
        # Enhance classes
        for cls in track(parsed_data['classes'], description="AI enhancing classes..."):
            try:
                ai_content = self.ai_generator.generate_class_examples(cls)
                enhanced_cls = {
                    'info': cls,
                    'ai_content': ai_content,
                    'enhanced_docstring': self.ai_generator.enhance_docstring(cls.docstring, cls.name)
                }
                enhanced_classes.append(enhanced_cls)
            except Exception as e:
                self.console.print(f"⚠️  AI enhancement failed for {cls.name}: {str(e)}", style="yellow")
                enhanced_classes.append({'info': cls, 'ai_content': {}, 'enhanced_docstring': cls.docstring})
        
        return {
            'functions': enhanced_functions,
            'classes': enhanced_classes,
            'total_items': len(enhanced_functions) + len(enhanced_classes)
        }
    
    def _generate_output(self, data: Dict[str, Any], output_path: str, format_type: str) -> Dict[str, Any]:
        """Generate output documentation files."""
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        generated_files = []
        
        if format_type.lower() == "html":
            html_file = output_dir / "documentation.html"
            self._generate_html(data, html_file)
            generated_files.append(str(html_file))
            
            # Generate CSS file
            css_file = output_dir / "style.css"
            self._generate_css(css_file)
            generated_files.append(str(css_file))
        
        elif format_type.lower() == "markdown":
            md_file = output_dir / "documentation.md"
            self._generate_markdown(data, md_file)
            generated_files.append(str(md_file))
        
        else:
            # Generate both
            html_file = output_dir / "documentation.html"
            md_file = output_dir / "documentation.md"
            css_file = output_dir / "style.css"
            
            self._generate_html(data, html_file)
            self._generate_markdown(data, md_file)
            self._generate_css(css_file)
            
            generated_files.extend([str(html_file), str(md_file), str(css_file)])
        
        # Generate JSON data file
        json_file = output_dir / "documentation_data.json"
        self._generate_json(data, json_file)
        generated_files.append(str(json_file))
        
        return {"files": generated_files, "output_dir": str(output_dir)}
    
    def _generate_html(self, data: Dict[str, Any], output_file: Path) -> None:
        """Generate HTML documentation."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 CodeDoc AI - Documentation</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-tomorrow.min.css" rel="stylesheet">
</head>
<body>
    <header>
        <h1>🚀 CodeDoc AI Documentation</h1>
        <p>Generated on {{ timestamp }}</p>
        <div class="stats">
            <span>📋 {{ total_functions }} Functions</span>
            <span>🏗️ {{ total_classes }} Classes</span>
            <span>🤖 AI Enhanced</span>
        </div>
    </header>

    <main>
        {% if functions %}
        <section class="functions-section">
            <h2>📋 Functions</h2>
            {% for func in functions %}
            <div class="code-item">
                <h3>{{ func.info.name }}</h3>
                <div class="docstring">{{ func.enhanced_docstring or func.info.docstring or 'No documentation' }}</div>
                
                <div class="signature">
                    <strong>Parameters:</strong> {{ func.info.args | join(', ') }}
                </div>
                
                {% if func.ai_content.explanation %}
                <div class="ai-explanation">
                    <h4>🤖 AI Explanation</h4>
                    <p>{{ func.ai_content.explanation }}</p>
                </div>
                {% endif %}
                
                {% if func.ai_content.examples %}
                <div class="examples">
                    <h4>💡 Examples</h4>
                    {% for example in func.ai_content.examples %}
                    <pre><code class="language-python">{{ example }}</code></pre>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if func.ai_content.use_cases %}
                <div class="use-cases">
                    <h4>🎯 Use Cases</h4>
                    <ul>
                    {% for use_case in func.ai_content.use_cases %}
                        <li>{{ use_case }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                <details class="source-code">
                    <summary>📄 Source Code</summary>
                    <pre><code class="language-python">{{ func.info.source_code }}</code></pre>
                </details>
            </div>
            {% endfor %}
        </section>
        {% endif %}
        
        {% if classes %}
        <section class="classes-section">
            <h2>🏗️ Classes</h2>
            {% for cls in classes %}
            <div class="code-item">
                <h3>{{ cls.info.name }}</h3>
                <div class="docstring">{{ cls.enhanced_docstring or cls.info.docstring or 'No documentation' }}</div>
                
                {% if cls.ai_content.explanation %}
                <div class="ai-explanation">
                    <h4>🤖 AI Explanation</h4>
                    <p>{{ cls.ai_content.explanation }}</p>
                </div>
                {% endif %}
                
                {% if cls.ai_content.examples %}
                <div class="examples">
                    <h4>💡 Examples</h4>
                    {% for example in cls.ai_content.examples %}
                    <pre><code class="language-python">{{ example }}</code></pre>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if cls.info.methods %}
                <div class="methods">
                    <h4>🔧 Methods</h4>
                    <ul>
                    {% for method in cls.info.methods %}
                        <li><strong>{{ method.name }}</strong>({{ method.args | join(', ') }})
                        {% if method.docstring %} - {{ method.docstring }}{% endif %}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
                
                <details class="source-code">
                    <summary>📄 Source Code</summary>
                    <pre><code class="language-python">{{ cls.info.source_code }}</code></pre>
                </details>
            </div>
            {% endfor %}
        </section>
        {% endif %}
    </main>
    
    <footer>
        <p>Generated by <strong>🚀 CodeDoc AI</strong> - The future of code documentation!</p>
    </footer>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            functions=data['functions'],
            classes=data['classes'],
            total_functions=len(data['functions']),
            total_classes=len(data['classes']),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        output_file.write_text(html_content, encoding='utf-8')
    
    def _generate_css(self, output_file: Path) -> None:
        """Generate CSS styles for HTML documentation."""
        css_content = """
/* 🚀 CodeDoc AI Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 1rem;
}

.stats span {
    background: #667eea;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
}

main {
    max-width: 1200px;
    margin: 2rem auto;
    padding: 0 2rem;
}

.functions-section, .classes-section {
    margin-bottom: 3rem;
}

.functions-section h2, .classes-section h2 {
    color: white;
    font-size: 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
}

.code-item {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.code-item h3 {
    color: #667eea;
    font-size: 1.5rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 0.5rem;
}

.docstring {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin-bottom: 1rem;
    font-style: italic;
}

.signature {
    background: #e9ecef;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-family: 'Monaco', 'Consolas', monospace;
}

.ai-explanation {
    background: linear-gradient(135deg, #667eea15, #764ba215);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border: 1px solid #667eea30;
}

.ai-explanation h4 {
    color: #667eea;
    margin-bottom: 0.5rem;
}

.examples {
    margin-bottom: 1rem;
}

.examples h4, .use-cases h4, .methods h4 {
    color: #495057;
    margin-bottom: 0.75rem;
}

.examples pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 0.5rem;
}

.use-cases ul, .methods ul {
    padding-left: 1.5rem;
}

.use-cases li, .methods li {
    margin-bottom: 0.5rem;
}

.source-code {
    margin-top: 1.5rem;
}

.source-code summary {
    cursor: pointer;
    color: #667eea;
    font-weight: bold;
    padding: 0.5rem;
    background: #f8f9fa;
    border-radius: 6px;
}

.source-code pre {
    background: #2d3748;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin-top: 0.5rem;
}

footer {
    text-align: center;
    padding: 2rem;
    color: white;
    background: rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

/* Responsive */
@media (max-width: 768px) {
    .stats {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    main {
        padding: 0 1rem;
    }
    
    .code-item {
        padding: 1rem;
    }
}
        """
        
        output_file.write_text(css_content, encoding='utf-8')
    
    def _generate_markdown(self, data: Dict[str, Any], output_file: Path) -> None:
        """Generate Markdown documentation."""
        md_content = f"""# 🚀 CodeDoc AI Documentation

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 **Statistics:** {len(data['functions'])} Functions, {len(data['classes'])} Classes

---

"""
        
        if data['functions']:
            md_content += "## 📋 Functions\n\n"
            for func in data['functions']:
                md_content += f"### {func['info'].name}\n\n"
                
                if func.get('enhanced_docstring') or func['info'].docstring:
                    md_content += f"**Description:** {func.get('enhanced_docstring') or func['info'].docstring}\n\n"
                
                md_content += f"**Parameters:** {', '.join(func['info'].args)}\n\n"
                
                if func.get('ai_content', {}).get('explanation'):
                    md_content += f"**🤖 AI Explanation:** {func['ai_content']['explanation']}\n\n"
                
                if func.get('ai_content', {}).get('examples'):
                    md_content += "**💡 Examples:**\n\n"
                    for example in func['ai_content']['examples']:
                        md_content += f"```python\n{example}\n```\n\n"
                
                if func.get('ai_content', {}).get('use_cases'):
                    md_content += "**🎯 Use Cases:**\n"
                    for use_case in func['ai_content']['use_cases']:
                        md_content += f"- {use_case}\n"
                    md_content += "\n"
                
                md_content += "<details>\n<summary>📄 Source Code</summary>\n\n"
                md_content += f"```python\n{func['info'].source_code}\n```\n\n</details>\n\n---\n\n"
        
        if data['classes']:
            md_content += "## 🏗️ Classes\n\n"
            for cls in data['classes']:
                md_content += f"### {cls['info'].name}\n\n"
                
                if cls.get('enhanced_docstring') or cls['info'].docstring:
                    md_content += f"**Description:** {cls.get('enhanced_docstring') or cls['info'].docstring}\n\n"
                
                if cls.get('ai_content', {}).get('explanation'):
                    md_content += f"**🤖 AI Explanation:** {cls['ai_content']['explanation']}\n\n"
                
                if cls.get('ai_content', {}).get('examples'):
                    md_content += "**💡 Examples:**\n\n"
                    for example in cls['ai_content']['examples']:
                        md_content += f"```python\n{example}\n```\n\n"
                
                if cls['info'].methods:
                    md_content += "**🔧 Methods:**\n"
                    for method in cls['info'].methods:
                        md_content += f"- **{method.name}**({', '.join(method.args)})"
                        if method.docstring:
                            md_content += f" - {method.docstring}"
                        md_content += "\n"
                    md_content += "\n"
                
                md_content += "<details>\n<summary>📄 Source Code</summary>\n\n"
                md_content += f"```python\n{cls['info'].source_code}\n```\n\n</details>\n\n---\n\n"
        
        md_content += "\n---\n*Generated by **🚀 CodeDoc AI** - The future of code documentation!*"
        
        output_file.write_text(md_content, encoding='utf-8')
    
    def _generate_json(self, data: Dict[str, Any], output_file: Path) -> None:
        """Generate JSON data file for programmatic access."""
        # Convert dataclass objects to dictionaries for JSON serialization
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'CodeDoc AI',
                'version': '0.1.0'
            },
            'summary': {
                'total_functions': len(data['functions']),
                'total_classes': len(data['classes']),
                'total_items': data['total_items']
            },
            'functions': [],
            'classes': []
        }
        
        for func in data['functions']:
            func_data = {
                'name': func['info'].name,
                'args': func['info'].args,
                'docstring': func['info'].docstring,
                'enhanced_docstring': func.get('enhanced_docstring'),
                'line_number': func['info'].line_number,
                'return_annotation': func['info'].return_annotation,
                'arg_annotations': func['info'].arg_annotations,
                'ai_content': func.get('ai_content', {})
            }
            json_data['functions'].append(func_data)
        
        for cls in data['classes']:
            cls_data = {
                'name': cls['info'].name,
                'docstring': cls['info'].docstring,
                'enhanced_docstring': cls.get('enhanced_docstring'),
                'line_number': cls['info'].line_number,
                'bases': cls['info'].bases,
                'methods': [
                    {
                        'name': method.name,
                        'args': method.args,
                        'docstring': method.docstring,
                        'line_number': method.line_number,
                        'return_annotation': method.return_annotation,
                        'arg_annotations': method.arg_annotations
                    }
                    for method in cls['info'].methods
                ],
                'ai_content': cls.get('ai_content', {})
            }
            json_data['classes'].append(cls_data)
        
        output_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding='utf-8') 