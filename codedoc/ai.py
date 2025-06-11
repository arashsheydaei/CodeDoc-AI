"""
AI Example Generator Module 🤖

Uses AI to generate smart examples, explanations, and use cases.
"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .parser import FunctionInfo, ClassInfo
import json


class AIExampleGenerator:
    """🤖 AI-powered example generator for code documentation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI generator with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise Exception("❌ OpenAI API key not found! Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
    
    def generate_function_examples(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate comprehensive examples for a function."""
        prompt = self._create_function_prompt(function)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a expert Python documentation generator. Generate practical, real-world examples and explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return self._parse_ai_response(result)
            
        except Exception as e:
            return {
                "examples": [f"# Example usage of {function.name}\nresult = {function.name}()"],
                "explanation": f"Function {function.name} with parameters: {', '.join(function.args)}",
                "use_cases": ["General purpose function"],
                "error": str(e)
            }
    
    def generate_class_examples(self, class_info: ClassInfo) -> Dict[str, Any]:
        """Generate comprehensive examples for a class."""
        prompt = self._create_class_prompt(class_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a expert Python documentation generator. Generate practical, real-world examples and explanations for classes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            result = response.choices[0].message.content
            return self._parse_ai_response(result)
            
        except Exception as e:
            return {
                "examples": [f"# Example usage of {class_info.name}\nobj = {class_info.name}()"],
                "explanation": f"Class {class_info.name} with {len(class_info.methods)} methods",
                "use_cases": ["General purpose class"],
                "error": str(e)
            }
    
    def _create_function_prompt(self, function: FunctionInfo) -> str:
        """Create a prompt for function documentation generation."""
        prompt = f"""
Generate comprehensive documentation for this Python function:

Function Name: {function.name}
Arguments: {', '.join(function.args)}
Docstring: {function.docstring or 'No docstring provided'}
Source Code:
```python
{function.source_code}
```

Please provide:
1. **Examples**: 2-3 practical code examples showing how to use this function
2. **Explanation**: Clear explanation of what the function does and when to use it  
3. **Use Cases**: Real-world scenarios where this function would be useful
4. **Parameters**: Detailed explanation of each parameter
5. **Return Value**: What the function returns

Format your response as JSON with keys: examples, explanation, use_cases, parameters, return_value
Make the examples practical and ready-to-run.
"""
        return prompt
    
    def _create_class_prompt(self, class_info: ClassInfo) -> str:
        """Create a prompt for class documentation generation."""
        methods_info = "\n".join([f"- {method.name}({', '.join(method.args)})" for method in class_info.methods])
        
        prompt = f"""
Generate comprehensive documentation for this Python class:

Class Name: {class_info.name}
Docstring: {class_info.docstring or 'No docstring provided'}
Methods: 
{methods_info}

Source Code:
```python
{class_info.source_code}
```

Please provide:
1. **Examples**: 2-3 practical code examples showing how to use this class
2. **Explanation**: Clear explanation of what the class does and its purpose
3. **Use Cases**: Real-world scenarios where this class would be useful
4. **Methods**: Brief explanation of key methods
5. **Attributes**: Important attributes if visible

Format your response as JSON with keys: examples, explanation, use_cases, methods, attributes
Make the examples practical and show real usage patterns.
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured information."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, parse manually
            result = {
                "examples": [],
                "explanation": "",
                "use_cases": [],
                "parameters": {},
                "return_value": ""
            }
            
            lines = response.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if 'example' in line.lower() and ':' in line:
                    current_section = 'examples'
                elif 'explanation' in line.lower() and ':' in line:
                    current_section = 'explanation'
                elif 'use case' in line.lower() and ':' in line:
                    current_section = 'use_cases'
                elif line.startswith('```python'):
                    current_content = []
                elif line.startswith('```'):
                    if current_section == 'examples' and current_content:
                        result['examples'].append('\n'.join(current_content))
                    current_content = []
                elif current_section and line:
                    if current_section == 'examples' and not line.startswith('#'):
                        current_content.append(line)
                    elif current_section == 'explanation':
                        result['explanation'] += line + ' '
                    elif current_section == 'use_cases' and line.startswith('-'):
                        result['use_cases'].append(line[1:].strip())
            
            # Ensure we have at least some content
            if not result['examples']:
                result['examples'] = ["# Add your example here"]
            if not result['explanation']:
                result['explanation'] = "Documentation generated by AI"
            
            return result
            
        except Exception as e:
            return {
                "examples": ["# AI parsing error"],
                "explanation": f"Error parsing AI response: {str(e)}",
                "use_cases": ["Error in generation"],
                "raw_response": response
            }
    
    def enhance_docstring(self, original_docstring: Optional[str], function_name: str) -> str:
        """Enhance an existing docstring with AI suggestions."""
        if not original_docstring:
            return f"Enhanced documentation for {function_name} (generated by AI)"
        
        prompt = f"""
Improve this docstring to be more helpful and comprehensive:

Original: {original_docstring}
Function: {function_name}

Make it:
- More descriptive
- Include parameter types if possible  
- Add usage examples if helpful
- Keep it concise but informative

Return only the improved docstring.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a documentation expert. Improve docstrings to be clear and helpful."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return original_docstring or f"Documentation for {function_name}" 