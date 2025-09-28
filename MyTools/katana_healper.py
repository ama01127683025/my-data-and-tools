#!/usr/bin/env python3
"""
URL Organizer and Directory Map Builder
Organizes URLs by file extension and builds directory structure maps
"""

import argparse
import re
from urllib.parse import urlparse, unquote
import os
from collections import defaultdict
import sys

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Organize URLs by file extension and build directory maps')
    parser.add_argument('-i', '--input', required=True, help='Input file containing URLs')
    parser.add_argument('-o', '--output', required=True, help='Output file for organized results')
    return parser.parse_args()

def extract_extension(url):
    """Extract file extension from URL"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    # Handle URLs without extensions
    if '.' not in path.split('/')[-1]:
        return 'no-extension'
    
    # Extract extension (last part after last dot)
    filename = path.split('/')[-1]
    if '.' in filename:
        return filename.split('.')[-1].lower()
    return 'no-extension'

def build_directory_map(urls):
    """Build a hierarchical directory map from URLs without duplicates"""
    dir_structure = defaultdict(lambda: defaultdict(set))
    
    for url in urls:
        parsed = urlparse(url)
        path = unquote(parsed.path)
        
        # Remove leading/trailing slashes and split
        clean_path = path.strip('/')
        parts = clean_path.split('/') if clean_path else []
        
        current_path = ""
        for i, part in enumerate(parts):
            if i == len(parts) - 1 and '.' in part:
                # This is a file - add to current directory
                dir_structure[current_path]['files'].add(part)
            else:
                # This is a directory - add to parent directory's subdirectories
                if part:  # Skip empty directory names
                    dir_structure[current_path]['dirs'].add(part)
                    current_path = os.path.join(current_path, part).replace('\\', '/')
    
    return dir_structure

def read_urls(input_file):
    """Read and clean URLs from input file"""
    urls = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    return urls

def print_directory_tree(dir_structure, current_path="", prefix="", f=None):
    """Recursively print directory tree structure"""
    # Get directories and files for current path
    dirs = sorted(dir_structure[current_path]['dirs'])
    files = sorted(dir_structure[current_path]['files'])
    
    # Print directories
    for i, dir_name in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1) and (len(files) == 0)
        connector = "└── " if is_last_dir else "├── "
        
        f.write(f"{prefix}{connector}{dir_name}/\n")
        
        # Determine prefix for next level
        new_prefix = prefix + ("    " if is_last_dir else "│   ")
        
        # Build next path and recurse
        next_path = os.path.join(current_path, dir_name).replace('\\', '/')
        print_directory_tree(dir_structure, next_path, new_prefix, f)
    
    # Print files
    for i, file_name in enumerate(files):
        is_last = i == len(files) - 1
        connector = "└── " if is_last else "├── "
        f.write(f"{prefix}{connector}{file_name}\n")

def write_output(output_file, extension_groups, dir_structure):
    """Write organized results to output file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("=" * 80 + "\n")
            f.write("URL ORGANIZER AND DIRECTORY MAP BUILDER\n")
            f.write("=" * 80 + "\n\n")
            
            # Write URLs organized by extension
            f.write("URLS ORGANIZED BY FILE EXTENSION\n")
            f.write("=" * 50 + "\n\n")
            
            total_urls = sum(len(urls) for urls in extension_groups.values())
            f.write(f"Total URLs processed: {total_urls}\n\n")
            
            for ext, urls in sorted(extension_groups.items()):
                if ext == 'no-extension':
                    f.write(f"URLS WITH NO EXTENSION ({len(urls)} URLs):\n")
                else:
                    f.write(f"{ext.upper()} FILES ({len(urls)} URLs):\n")
                f.write("-" * 40 + "\n")
                
                for url in sorted(urls):
                    f.write(f"{url}\n")
                f.write("\n" + "=" * 50 + "\n\n")
            
            # Write directory map
            f.write("DIRECTORY STRUCTURE MAP\n")
            f.write("=" * 50 + "\n\n")
            
            if dir_structure:
                f.write("Directory Tree:\n")
                f.write(".\n")
                print_directory_tree(dir_structure, "", "", f)
            else:
                f.write("No directory structure could be extracted from the URLs.\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    """Main function"""
    args = parse_arguments()
    
    print(f"[+] Reading URLs from: {args.input}")
    urls = read_urls(args.input)
    print(f"[+] Found {len(urls)} URLs")
    
    # Organize URLs by extension
    print("[+] Organizing URLs by file extension...")
    extension_groups = defaultdict(list)
    for url in urls:
        ext = extract_extension(url)
        extension_groups[ext].append(url)
    
    # Build directory structure
    print("[+] Building directory structure map...")
    dir_structure = build_directory_map(urls)
    
    # Write output
    print(f"[+] Writing results to: {args.output}")
    write_output(args.output, extension_groups, dir_structure)
    
    # Print summary
    print("\n[+] Organization Complete!")
    print(f"    - Input file: {args.input}")
    print(f"    - Output file: {args.output}")
    print(f"    - Total URLs processed: {len(urls)}")
    print(f"    - File extension groups: {len(extension_groups)}")
    
    print("\n[+] Extension Summary:")
    for ext, urls_list in sorted(extension_groups.items()):
        if ext == 'no-extension':
            print(f"    - URLs with no extension: {len(urls_list)}")
        else:
            print(f"    - {ext.upper()} files: {len(urls_list)}")

if __name__ == "__main__":
    main()