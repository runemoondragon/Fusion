from tools.base import BaseTool
import os
import json
from typing import Union, List, Dict
from pathlib import Path
import logging # Added for logging

class FileCreatorTool(BaseTool):
    name = "filecreatortool"
    description = '''
    Creates new files with specified content.
    
    IMPORTANT: The input must follow this exact structure:
    1. For a single file:
       {
           "files": {
               "path": "path/to/file.txt",
               "content": "file content here"
           }
       }
    
    2. For multiple files:
       {
           "files": [
               {
                   "path": "path/to/file1.txt",
                   "content": "content for file 1"
               },
               {
                   "path": "path/to/file2.txt",
                   "content": "content for file 2"
               }
           ]
       }
    
    Features:
    - Creates parent directories automatically if they don't exist
    - Supports both text and binary content
    - Can create multiple files in one call
    - Handles JSON content automatically
    
    Optional parameters:
    - binary: boolean (default: false) - Set to true for binary files
    - encoding: string (default: "utf-8") - Specify file encoding
    
    Example usage:
    1. Create a Python file:
       {
           "files": {
               "path": "test.py",
               "content": "def hello():\\n    print('Hello, World!')"
           }
       }
    
    2. Create multiple files:
       {
           "files": [
               {
                   "path": "src/main.py",
                   "content": "# Main file content"
               },
               {
                   "path": "src/utils.py",
                   "content": "# Utils file content"
               }
           ]
       }
    '''
    input_schema = {
        "type": "object",
        "properties": {
            "files": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"oneOf": [{"type": "string"}, {"type": "object"}]},
                            "binary": {"type": "boolean", "default": False},
                            "encoding": {"type": "string", "default": "utf-8"}
                        },
                        "required": ["path", "content"]
                    },
                    {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"oneOf": [{"type": "string"}, {"type": "object"}]},
                                "binary": {"type": "boolean", "default": False},
                                "encoding": {"type": "string", "default": "utf-8"}
                            },
                            "required": ["path", "content"]
                        }
                    }
                ]
            }
        },
        "required": ["files"]
    }

    def execute(self, **kwargs) -> str:
        """
        Execute the file creation process.
        
        Args:
            **kwargs: Must contain 'files' key with either a dict or list of dicts
                     Each dict must have 'path' and 'content' keys
        
        Returns:
            str: JSON string containing results of file creation operations
        """
        files_arg_value = kwargs.get('files')

        # Gemini-specific correction for over-nesting
        if (isinstance(files_arg_value, dict) and
           len(files_arg_value) == 1 and
           'files' in files_arg_value and
           (isinstance(files_arg_value['files'], dict) or isinstance(files_arg_value['files'], list))):
            
            potential_actual_specs = files_arg_value['files']
            is_single_spec_like = (isinstance(potential_actual_specs, dict) and
                                   'path' in potential_actual_specs and
                                   'content' in potential_actual_specs) # content can be an empty string or dict
            
            is_list_of_specs_like = False
            if isinstance(potential_actual_specs, list):
                if not potential_actual_specs: # Empty list is a valid structure for 'files' to mean no files
                    is_list_of_specs_like = True
                elif (potential_actual_specs and # Ensure list is not empty before accessing [0]
                      isinstance(potential_actual_specs[0], dict) and
                      'path' in potential_actual_specs[0] and
                      'content' in potential_actual_specs[0]):
                    is_list_of_specs_like = True

            if is_single_spec_like or is_list_of_specs_like:
                try:
                    logger = getattr(self, 'logger', logging.getLogger(__name__))
                    logger.info(
                        "FileCreatorTool: Correcting over-nested 'files' argument (Gemini-specific)."
                    )
                except Exception: # Broad exception to ensure logging doesn't break execution
                    print("FileCreatorTool: Correcting over-nested 'files' argument (logging failed).")
                files_arg_value = potential_actual_specs

        processed_file_specs = []
        if files_arg_value is None:
            processed_file_specs = []
        elif isinstance(files_arg_value, dict):
            processed_file_specs = [files_arg_value]
        elif isinstance(files_arg_value, list):
            processed_file_specs = files_arg_value
        else:
            return json.dumps({
                'created_files': 0, 'failed_files': 1,
                'results': [{'path': None, 'success': False, 'error': f"Invalid type for 'files' argument: {type(files_arg_value)}"}]
            }, indent=2)

        results = []
        if not processed_file_specs:
            results.append({
                'path': None,
                'success': False,
                'error': "No file specifications provided or argument was invalid."
            })
        
        for file_spec in processed_file_specs:
            path_str = None 
            try:
                if not isinstance(file_spec, dict):
                    results.append({'path': None, 'success': False, 'error': f'Invalid file spec type: {type(file_spec)}. Expected dict.'})
                    continue

                path_str = file_spec.get('path')
                content = file_spec.get('content') 

                if not path_str:
                    results.append({'path': None, 'success': False, 'error': "Missing 'path' in file spec."})
                    continue
                
                # 'content' is required by the schema for each file item.
                # It can be an empty string or an empty dict, but not None.
                if content is None:
                     results.append({'path': path_str, 'success': False, 'error': "Missing 'content' in file spec."})
                     continue

                path = Path(path_str)
                binary = file_spec.get('binary', False)
                encoding = file_spec.get('encoding', 'utf-8')

                # Create parent directories
                path.parent.mkdir(parents=True, exist_ok=True)

                # Handle content
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)

                # Write file
                mode = 'wb' if binary else 'w'
                if binary:
                    if isinstance(content, str):
                        content = content.encode(encoding)
                    with open(path, mode) as f:
                        f.write(content)
                else:
                    with open(path, mode, encoding=encoding, newline='') as f:
                        f.write(content)

                results.append({
                    'path': str(path),
                    'success': True,
                    'size': path.stat().st_size
                })

            except Exception as e:
                results.append({
                    'path': str(path) if 'path' in locals() and path is not None else path_str if path_str is not None else None,
                    'success': False,
                    'error': str(e)
                })

        return json.dumps({
            'created_files': len([r for r in results if r['success']]),
            'failed_files': len([r for r in results if not r['success']]),
            'results': results
        }, indent=2)