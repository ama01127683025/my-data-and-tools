#!/usr/bin/env python3
"""
GitHub Dorking Tool
Searches GitHub using predefined dorks from org.txt or domain.txt files
"""

import argparse
import os
import sys
import urllib.parse

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def load_dork_file(file_path, search_term):
    """
    Load dork patterns from file and replace the placeholder with search term
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace placeholder based on file type
        if "org.txt" in file_path:
            # Replace org:example with org:search_term
            content = content.replace("org:example", f"org:{search_term}")
        elif "domain.txt" in file_path:
            # Replace "example.com" with the actual domain
            content = content.replace('"example.com"', f'"{search_term}"')
        
        # Split into individual dorks
        dorks = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        return dorks
    except FileNotFoundError:
        print(f"{Colors.RED}Error: Dork file '{file_path}' not found.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error reading dork file: {e}{Colors.END}")
        sys.exit(1)

def generate_github_url(dork):
    """
    Generate GitHub search URL from dork
    """
    # URL encode the dork
    encoded_dork = urllib.parse.quote(dork)
    return f"https://github.com/search?q={encoded_dork}&type=code"

def print_colored(text, color=Colors.END):
    """Print colored text"""
    print(f"{color}{text}{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description='GitHub Dorking Tool')
    parser.add_argument('-org', type=str, help='Search by organization name')
    parser.add_argument('-domain', type=str, help='Search by domain name')
    parser.add_argument('-o', '--output', type=str, help='Output file path to save URLs')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.org and not args.domain:
        parser.error("Either -org or -domain must be specified")
    
    if args.org and args.domain:
        parser.error("Cannot use both -org and -domain simultaneously")
    
    # Determine search type and load appropriate dork file
    if args.org:
        search_type = "org"
        search_term = args.org
        dork_file = "org.txt"
    else:
        search_type = "domain"
        search_term = args.domain
        dork_file = "domain.txt"
    
    # Check if dork file exists
    if not os.path.exists(dork_file):
        print_colored(f"Error: Dork file '{dork_file}' not found in current directory.", Colors.RED)
        print_colored("Please make sure org.txt and domain.txt are in the same directory as this script.", Colors.RED)
        sys.exit(1)
    
    print_colored("🔍 GitHub Dorking Tool", Colors.BOLD + Colors.GREEN)
    print_colored(f"📁 Search Type: {search_type}", Colors.YELLOW)
    print_colored(f"🔎 Search Term: {search_term}", Colors.YELLOW)
    print_colored(f"📄 Using dork file: {dork_file}", Colors.YELLOW)
    print_colored("=" * 60, Colors.BLUE)
    print()
    
    # Load and process dorks
    dorks = load_dork_file(dork_file, search_term)
    
    print_colored(f"📋 Loaded {len(dorks)} dork patterns", Colors.GREEN)
    print()
    
    # Generate URLs
    urls = []
    for i, dork in enumerate(dorks, 1):
        url = generate_github_url(dork)
        urls.append(url)
        
        # Print dork in yellow
        print_colored(f"{i:2d}. {dork}", Colors.YELLOW)
        # Print URL in blue
        print_colored(f"    🔗 {url}", Colors.BLUE)
        print()
    
    # Save to file if output specified
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"# GitHub Dorking Results\n")
                f.write(f"# Search Type: {search_type}\n")
                f.write(f"# Search Term: {search_term}\n")
                f.write(f"# Total URLs: {len(urls)}\n")
                f.write("\n".join(urls))
            
            print_colored(f"💾 URLs saved to: {args.output}", Colors.GREEN)
        except Exception as e:
            print_colored(f"Error saving to file: {e}", Colors.RED)
    
    print_colored("🎯 Search completed! Copy and paste the URLs in your browser to view results.", Colors.BOLD + Colors.GREEN)

if __name__ == "__main__":
    main()