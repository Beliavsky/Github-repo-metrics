from bs4 import BeautifulSoup
import re
import requests
import os
import time
import ast
from datetime import datetime

# GitHub API token handling
TOKEN_FILE = "github_token.txt"  # File to read token from
def load_github_token():
    """Load GitHub token from file or environment variable."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return os.getenv("GITHUB_TOKEN")  # Fallback to environment variable

GITHUB_TOKEN = load_github_token()
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def github_stars(repo_url, method="page"):
    if method == "page":
        return github_stars_from_page(repo_url)
    else:
        return github_stars_from_api(repo_url)

def github_stars_from_api(repo_url):
    """Fetch the number of stars for a GitHub repository using the API."""
    match = re.search(r'github\.com/([^/]+/[^/]+)', repo_url)
    if not match:
        return 0
    repo_path = match.group(1).replace('/blob/main', '')
    api_url = f"https://api.github.com/repos/{repo_path}"
    
    try:
        response = requests.get(api_url, headers=HEADERS)
        if 400 <= response.status_code <= 499:  # Client errors
            raise requests.exceptions.HTTPError(f"{response.status_code} Client Error: {response.reason}")
        response.raise_for_status()
        data = response.json()
        return data.get("stargazers_count", 0)
    except requests.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and "Client Error" in str(e):
            raise  # Re-raise client errors to be caught upstream
        print(f"Warning: Could not fetch stars for {repo_url}: {e}")
        return 0
    finally:
        time.sleep(0.1)

def github_stars_from_page(repo_url, sleep_time=0.1):
    """
    Fetch the number of stars for a GitHub repository by scraping its webpage.
    
    Args:
        repo_url (str): The URL of the GitHub repository (e.g., 'https://github.com/spacepy/spacepy')
    
    Returns:
        int: Number of stars, or -1 if the fetch fails or stars can't be found
    """
    try:
        # Set a user-agent to mimic a browser and avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(repo_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the stars element - GitHub uses a link with 'stargazers' in the href
        star_link = soup.find('a', href=re.compile(r'/stargazers$'))
        if not star_link:
            return -1
        
        # Extract the text containing the star count (e.g., "242" or "1.2k")
        star_text = star_link.get_text(strip=True)
        
        # Clean the text to extract only the numeric part
        # Match numbers (possibly with 'k' or commas)
        match = re.search(r'([\d,.]+k?)', star_text, re.IGNORECASE)
        if not match:
            return -1
        star_count = match.group(1)
        
        # Convert to integer (handle 'k' for thousands)
        if 'k' in star_count.lower():
            # Convert e.g., "1.2k" to 1200
            num = float(star_count.lower().replace('k', ''))
            return int(num * 1000)
        return int(star_count.replace(',', ''))  # Remove commas for numbers like "1,234"
    
    except (requests.RequestException, ValueError, AttributeError) as e:
        print(f"Error fetching stars for {repo_url}: {e}")
        return -1    
    finally:
        time.sleep(sleep_time)  # Add a delay after each request

def repo_data(repo_url, sleep_time=0.1):
    """
    Fetch information about a GitHub repository by scraping its webpage.
    
    Args:
        repo_url (str): The URL of the GitHub repository (e.g., 'https://github.com/Beliavsky/R_and_Fortran')
        sleep_time (float): Time in seconds to sleep after the request (default: 0.1)
    
    Returns:
        dict: Dictionary containing 'stars' (int), 'license' (str or None), and 'topics' (list of str),
              or {'stars': -1, 'license': None, 'topics': []} if the fetch fails
    """
    # Default return value in case of failure
    default_data = {'stars': -1, 'license': None, 'topics': []}
    
    try:
        # Set a user-agent to mimic a browser and avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(repo_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize data dictionary
        data = {'stars': -1, 'license': None, 'topics': []}
        
        # Fetch stars (link with 'stargazers' in href)
        star_link = soup.find('a', href=re.compile(r'/stargazers$'))
        if star_link:
            star_text = star_link.get_text(strip=True)
            match = re.search(r'([\d,.]+k?)', star_text, re.IGNORECASE)
            if match:
                star_count = match.group(1)
                if 'k' in star_count.lower():
                    num = float(star_count.lower().replace('k', ''))
                    data['stars'] = int(num * 1000)
                else:
                    data['stars'] = int(star_count.replace(',', ''))
        
        # Fetch license (look for 'License' text or specific license link)
        license_section = soup.find('span', string=re.compile(r'License', re.I))
        if license_section:
            # License is usually in a sibling or nearby element
            license_link = license_section.find_parent('a') or license_section.find_next('a')
            if license_link:
                license_text = license_link.get_text(strip=True)
                data['license'] = license_text if license_text else None
        else:
            # Alternative: look for a direct license file link
            license_file = soup.find('a', href=re.compile(r'/LICENSE$', re.I))
            if license_file:
                data['license'] = license_file.get_text(strip=True) or 'Unknown'
        
        # Fetch topics (elements with class 'topic-tag' or similar)
        topic_elements = soup.find_all('a', class_=re.compile(r'topic-tag'))
        if topic_elements:
            data['topics'] = [topic.get_text(strip=True) for topic in topic_elements if topic.get_text(strip=True)]
        
        return data
    
    except (requests.RequestException, ValueError, AttributeError) as e:
        print(f"Error fetching data for {repo_url}: {e}")
        return default_data
    
    finally:
        time.sleep(sleep_time)  # Use the sleep_time argument

def read_repo_data(file_path):
    """
    Read repository data from a file and store it in a dictionary.
    
    Args:
        file_path (str): Path to the file containing repository data
    
    Returns:
        dict: Dictionary with repo URLs as keys and sub-dictionaries with 'stars', 'license', 'topics' as values
              Returns empty dict if file reading fails
    """
    repo_data = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_url = None
        current_data = {}
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                if current_url and current_data:  # Save previous entry if complete
                    repo_data[current_url] = current_data
                    current_data = {}
                continue
            
            # Check if line is a URL
            if line.startswith('https://github.com/'):
                if current_url and current_data:  # Save previous entry before starting new one
                    repo_data[current_url] = current_data
                    current_data = {}
                current_url = line
            elif line.startswith('stars '):
                current_data['stars'] = int(line.replace('stars ', ''))
            elif line.startswith('license '):
                license_text = line.replace('license ', '')
                current_data['license'] = license_text if license_text != 'None' else None
            elif line.startswith('topics '):
                # Parse the topics list string into an actual list
                topics_str = line.replace('topics ', '')
                current_data['topics'] = ast.literal_eval(topics_str)
        
        # Save the last entry if it exists
        if current_url and current_data:
            repo_data[current_url] = current_data
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return {}
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing file '{file_path}': {e}")
        return {}
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return {}    
    return repo_data

def topics_to_repos(repo_dict):
    """
    Create a dictionary mapping topics to lists of repository URLs that have that topic.
    
    Args:
        repo_dict (dict): Dictionary with repo URLs as keys and sub-dictionaries 
                         containing 'stars', 'license', 'topics' as values
    
    Returns:
        dict: Dictionary with topics as keys and lists of repo URLs as values
    """
    topic_map = {}
    
    # Iterate over each repo and its data
    for repo_url, data in repo_dict.items():
        # Get the topics list, default to empty list if missing
        topics = data.get('topics', [])
        
        # Add the repo URL to the list for each topic
        for topic in topics:
            if topic in topic_map:
                topic_map[topic].append(repo_url)
            else:
                topic_map[topic] = [repo_url]    
    return topic_map

def repo_creation_date_api(owner, repo, token=None):
    """
    Get the creation date of a GitHub repository using the GitHub API.
    
    Args:
        owner (str): Repository owner (e.g., 'ef1j')
        repo (str): Repository name (e.g., 'Art1')
        token (str, optional): GitHub personal access token for higher rate limits
    
    Returns:
        datetime: Creation date of the repo, or None if fetch fails
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            print(f"Rate limit exceeded for {url}. Consider using a token or waiting.")
            return None
        response.raise_for_status()
        
        data = response.json()
        created_at = data.get("created_at")
        if created_at:
            return datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
        return None
    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None
    
    finally:
        time.sleep(1)  # Be polite to GitHub servers

def repo_info(owner, repo, token=None):
    """
    Fetch all available fields for a GitHub repository using the GitHub API.
    
    Args:
        owner (str): Repository owner (e.g., 'ef1j')
        repo (str): Repository name (e.g., 'Art1')
        token (str, optional): GitHub personal access token for higher rate limits
    
    Returns:
        dict: Dictionary containing all fields from the API response,
              or an empty dict if the fetch fails
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            print(f"Rate limit exceeded for {url}. Consider using a token or waiting.")
            return {}
        elif response.status_code == 404:
            print(f"Repository not found: {owner}/{repo}")
            return {}
        response.raise_for_status()
        
        # Return the full JSON response as a dictionary
        data = response.json()
        print(f"Successfully fetched data for {owner}/{repo}")
        return data
    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {}    
    finally:
        time.sleep(1)  # Be polite to GitHub servers
