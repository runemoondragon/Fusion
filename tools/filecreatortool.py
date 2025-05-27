from tools.base import BaseTool
import os
import json
from typing import Union, List, Dict
from pathlib import Path
import logging # Added for logging
from werkzeug.utils import secure_filename # Added
from config import Config # Added

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
            request_id: The unique identifier for the current request/session.
            **kwargs: Must contain 'files' key with either a dict or list of dicts
                     Each dict must have 'path' and 'content' keys. 'path' is expected to be a filename.
        
        Returns:
            str: JSON string containing results of file creation operations
        """
        # Extract request_id which is now a named argument, not in kwargs
        request_id = kwargs.pop("request_id", None)
        if not request_id:
            return json.dumps({
                'created_files': 0, 'failed_files': 0, # Assuming 0 files if request_id is missing
                'results': [{'path': None, 'success': False, 'error': "Critical: request_id was not provided to FileCreatorTool."}]
            }, indent=2)

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
            original_input_filename = None # To store the filename LLM intended
            try:
                if not isinstance(file_spec, dict):
                    results.append({'path': None, 'success': False, 'error': f'Invalid file spec type: {type(file_spec)}. Expected dict.'})
                    continue

                original_input_filename = file_spec.get('path') # This is now treated as a filename
                content = file_spec.get('content') 

                if not original_input_filename:
                    results.append({'path': None, 'success': False, 'error': "Missing 'path' (expected filename) in file spec."})
                    continue
                
                if content is None:
                     results.append({'path': original_input_filename, 'success': False, 'error': "Missing 'content' in file spec."})
                     continue

                # Sanitize the filename provided by the LLM
                safe_filename = secure_filename(original_input_filename)
                if not safe_filename: # secure_filename returns empty if input is bad (e.g., just "..")
                    results.append({'path': original_input_filename, 'success': False, 'error': f"Invalid filename provided: '{original_input_filename}'. Could not be secured."})
                    continue

                # Determine base directory from Config
                base_generated_files_dir = Path(getattr(Config, 'GENERATED_FILES_DIR', './generated_files')) # Default if not in Config
                
                # Create session-specific directory
                session_specific_dir = base_generated_files_dir / request_id
                session_specific_dir.mkdir(parents=True, exist_ok=True)

                # Final path for saving the file
                actual_save_path = session_specific_dir / safe_filename
                
                binary = file_spec.get('binary', False)
                encoding = file_spec.get('encoding', 'utf-8')

                # Create parent directories (already handled by session_specific_dir.mkdir)
                # actual_save_path.parent.mkdir(parents=True, exist_ok=True) # Redundant now

                # Handle content
                if isinstance(content, dict):
                    content = json.dumps(content, indent=2)

                # Write file
                mode = 'wb' if binary else 'w'
                if binary:
                    if isinstance(content, str):
                        content = content.encode(encoding)
                    with open(actual_save_path, mode) as f:
                        f.write(content)
                else:
                    with open(actual_save_path, mode, encoding=encoding, newline='') as f:
                        f.write(content)

                results.append({
                    'path': safe_filename, # Return only the secured filename
                    'original_input_path': original_input_filename, # For reference if needed
                    'full_server_path': str(actual_save_path), # For server-side logging/debugging
                    'success': True,
                    'size': actual_save_path.stat().st_size
                })

            except Exception as e:
                results.append({
                    'path': safe_filename if 'safe_filename' in locals() and safe_filename else original_input_filename,
                    'success': False,
                    'error': str(e)
                })

        return json.dumps({
            'created_files': len([r for r in results if r['success']]),
            'failed_files': len([r for r in results if not r['success']]),
            'results': results
        }, indent=2)