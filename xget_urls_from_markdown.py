import re

def extract_github_urls(markdown_file):
    """
    Extract the first GitHub URL from each repository entry in a markdown file.
    
    Args:
        markdown_file (str): Path to the markdown file
    
    Returns:
        list: List of first GitHub URLs found in each entry
    """
    github_urls = []
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process each line
        for line in lines:
            # Skip headers and non-entry lines
            if line.strip().startswith('#') or not line.strip().startswith('['):
                continue
            
            # Find the first GitHub URL in the line
            match = re.search(r'\((https://github\.com/[^\s)]+)\)', line)
            if match:
                github_urls.append(match.group(1))
    
    except FileNotFoundError:
        print(f"Error: File '{markdown_file}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{markdown_file}': {e}")
        return []
    
    return github_urls

# Example usage
if __name__ == "__main__":
    markdown_file = "repos.md"  # Replace with your file name
    urls = extract_github_urls(markdown_file)
    for url in urls:
        print(url)
