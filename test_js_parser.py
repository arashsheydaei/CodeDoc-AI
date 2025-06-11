#!/usr/bin/env python3
"""Test script for JavaScript parser."""

from codedoc.js_parser import JavaScriptParser
import json

def test_js_parser():
    """Test the JavaScript parser with demo.js file."""
    parser = JavaScriptParser()
    
    try:
        print("🔍 Testing JavaScript Parser...")
        result = parser.parse_file('demo.js')
        
        print('🎉 JavaScript parsing successful!')
        print(f'Functions found: {len(result.functions)}')
        print(f'Classes found: {len(result.classes)}')
        print(f'Imports: {len(result.imports)}')
        print(f'Exports: {len(result.exports)}')
        
        print('\n📋 Functions:')
        for func in result.functions[:3]:  # Show first 3
            print(f'  • {func.name}({", ".join(func.params)})')
            if func.docstring:
                print(f'    📝 {func.docstring[:80]}...')
            print(f'    🔧 Async: {func.is_async}, Arrow: {func.is_arrow_function}')
        
        print('\n🏗️ Classes:')
        for cls in result.classes:
            print(f'  • {cls.name} (methods: {len(cls.methods)})')
            if cls.docstring:
                print(f'    📝 {cls.docstring[:80]}...')
            if cls.extends:
                print(f'    🔗 Extends: {cls.extends}')
                
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_js_parser() 