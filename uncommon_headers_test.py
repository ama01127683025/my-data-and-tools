import requests
import re
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

# Configuration - Set these variables before running
HEADERS_FILE_PATH = "/home/kali/wordlist/uncommon_header.txt"  # Path to your headers file
HEADER_VALUE = "sadek"  # Value to assign to each header
REQUEST_TIMEOUT = 10  # Timeout in seconds for each request
ENABLE_CACHE_BUSTER = True  # Set to True to add cache-busting parameter to URLs

request_code = """
import httpx

client = httpx.Client(http2=True)
request_url = "https://thankyou.cablex.ch:8443/modules/grafana/service/api/access-control/roles"
request_headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "X-Api-Key": "a+X25PH05Pz9/fTk/Or05Pf16vX26v39/f3k9A==", "Content-Type": "application/json", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Priority": "u=0, i", "Te": "trailers"}
response = client.get(request_url, headers=request_headers)
"""

# ==============================================
# DO NOT EDIT BELOW THIS LINE UNLESS NECESSARY
# ==============================================

def add_cache_buster(url, counter):
    """Add cache-busting parameter to URL if ENABLE_CACHE_BUSTER is True"""
    if not ENABLE_CACHE_BUSTER:
        return url
    
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['test'] = [str(counter)]
    
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def extract_request_details(request_code):
    """Extract URL, headers, and other request details from the httpx-generated Python code"""
    try:
        # Extract URL
        url_match = re.search(r"request_url\s*=\s*[\"']([^\"']+)[\"']", request_code)
        if not url_match:
            raise ValueError("Could not find URL in request code")
        
        url = url_match.group(1)
        
        # Extract method (from the client call)
        method_match = re.search(r"client\.(get|post|put|delete|patch|head|options)\(", request_code, re.IGNORECASE)
        method = method_match.group(1).lower() if method_match else 'get'
        
        # Extract headers
        headers_match = re.search(r"request_headers\s*=\s*\{([^}]+)\}", request_code, re.DOTALL)
        original_headers = {}
        if headers_match:
            headers_str = headers_match.group(1)
            # Simple parsing of headers dictionary (won't handle all edge cases)
            for line in headers_str.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip().strip('\'"')
                value = value.strip().strip(',\'"')
                original_headers[key] = value
        
        # Extract cookies
        cookies_match = re.search(r"request_cookies\s*=\s*\{([^}]+)\}", request_code, re.DOTALL)
        cookies = {}
        if cookies_match:
            cookies_str = cookies_match.group(1)
            for line in cookies_str.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip().strip('\'"')
                value = value.strip().strip(',\'"')
                cookies[key] = value
        
        # Extract data if it's a POST/PUT/PATCH request
        data = None
        data_match = re.search(r"data\s*=\s*\{([^}]+)\}", request_code, re.DOTALL)
        if data_match:
            data_str = data_match.group(1)
            data = {}
            for line in data_str.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip().strip('\'"')
                value = value.strip().strip(',\'"')
                data[key] = value
        
        return {
            'method': method,
            'url': url,
            'original_headers': original_headers,
            'cookies': cookies,
            'data': data
        }
    except Exception as e:
        print(f"Error parsing request code: {e}")
        return None

def load_headers(file_path):
    """Load headers from file, one per line"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

def is_value_reflected(response, header_name, test_value):
    """Check if the test value is reflected in the response"""
    try:
        # Check response headers
        for resp_header_name, resp_header_value in response.headers.items():
            if test_value.lower() in resp_header_value.lower():
                return True
        
        # Check response body
        if test_value.lower() in response.text.lower():
            return True
            
        return False
    except:
        return False

def send_request(method, url, headers, cookies=None, data=None):
    """Send HTTP request with error handling"""
    try:
        if method == 'get':
            return requests.get(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'post':
            return requests.post(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'put':
            return requests.put(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'delete':
            return requests.delete(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'patch':
            return requests.patch(url, headers=headers, cookies=cookies, data=data, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'head':
            return requests.head(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT,verify=False)
        elif method == 'options':
            return requests.options(url, headers=headers, cookies=cookies, timeout=REQUEST_TIMEOUT,verify=False)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    # Read the request code from the variable above
    
    # Extract request details
    request_details = extract_request_details(request_code)
    if not request_details:
        print("Failed to parse request code. Please check the format.")
        return
    
    print(f"\nTarget URL: {request_details['url']}")
    print(f"Original Method: {request_details['method'].upper()}")
    print(f"Original Headers: {len(request_details['original_headers'])} headers")
    print(f"Original Cookies: {len(request_details['cookies'])} cookies")
    if request_details['data']:
        print(f"Request Data: {request_details['data']}")
    print(f"Testing with header value: '{HEADER_VALUE}'")
    print(f"Cache buster: {'ENABLED' if ENABLE_CACHE_BUSTER else 'DISABLED'}")
    print("="*80)
    
    # Load headers to test
    try:
        headers_to_test = load_headers(HEADERS_FILE_PATH)
    except FileNotFoundError:
        print(f"Error: Headers file not found at {HEADERS_FILE_PATH}")
        return
    
    print(f"Loaded {len(headers_to_test)} headers to test\n")
    
    # Test each header
    results = []
    reflected_headers = []
    status_codes = {}
    
    for i, header_name in enumerate(headers_to_test, 1):
        # Prepare headers - keep original ones and add our test header
        test_headers = request_details['original_headers'].copy()
        test_headers[header_name] = HEADER_VALUE
        
        # Add cache buster if enabled
        request_url = add_cache_buster(request_details['url'], i)
        
        # Send request
        print(f"Testing header {i}/{len(headers_to_test)}: {header_name}")
        response = send_request(
            request_details['method'],
            request_url,
            test_headers,
            request_details['cookies'],
            request_details['data']
        )
        
        if response is None:
            print("  -> Request failed\n")
            results.append((header_name, "FAILED", 0, False))
            continue
        
        # Check if value is reflected
        reflected = is_value_reflected(response, header_name, HEADER_VALUE)
        
        # Record status code
        status_code = response.status_code
        status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        # Record reflected headers
        if reflected:
            reflected_headers.append(header_name)
        
        # Store results
        results.append((
            header_name,
            status_code,
            len(response.content),
            reflected
        ))
        
        # Print current result
        print(f"  -> Status: {status_code}, Length: {len(response.content)}, Reflected: {reflected}\n")
    
    # Print summary
    print("\n" + "="*80)
    print("TESTING COMPLETE - SUMMARY")
    print("="*80)
    
    
    # Print detailed results
    print("\nDetailed Results:")
    print("-"*80)
    print("Header".ljust(30) + "Status".ljust(10) + "Length".ljust(10) + "Reflected")
    print("-"*80)
    for header, status, length, reflected in results:
        print(f"{header[:28].ljust(30)}{str(status).ljust(10)}{str(length).ljust(10)}{reflected}")
    # Print status code summary
    print("\nStatus Codes Received:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count} requests")
    
    # Print reflected headers
    print(f"\nHeaders with reflected values ({len(reflected_headers)}):")
    for header in reflected_headers:
        print(f"  {header}")

if __name__ == "__main__":
    main()