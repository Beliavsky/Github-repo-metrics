from collections import defaultdict
import ast

# Function to parse topic_lists.txt
def parse_topic_lists(file_path):
    topic_lists = {}
    current_topic = None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Check if line starts with a number (indicating a new topic)
            if line[0].isdigit():
                parts = line.split(maxsplit=2)
                if len(parts) >= 2:
                    current_topic = parts[1]
                    topic_lists[current_topic] = []
            elif current_topic and line.startswith("https://github.com"):
                topic_lists[current_topic].append(line)
    return topic_lists

# Function to parse repo_data.txt
def parse_repo_data(file_path):
    repos_data = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("https://github.com"):
                repo_url = line
                repo_info = {"stars": 0, "license": "N/A", "topics": []}
                i += 1
                while i < len(lines) and lines[i].strip():
                    info_line = lines[i].strip()
                    if info_line.startswith("stars"):
                        repo_info["stars"] = int(info_line.split()[1])
                    elif info_line.startswith("license"):
                        repo_info["license"] = " ".join(info_line.split()[1:])
                    elif info_line.startswith("topics"):
                        # Safely parse the topics list as a Python literal
                        topics_str = " ".join(info_line.split()[1:])
                        repo_info["topics"] = ast.literal_eval(topics_str)
                    i += 1
                repos_data[repo_url] = repo_info
            else:
                i += 1
    return repos_data

# Main processing
def process_and_sort_repos(topic_lists_file, repo_data_file):
    # Parse the input files
    topic_lists = parse_topic_lists(topic_lists_file)
    repos_data = parse_repo_data(repo_data_file)

    # Create a dictionary to store repos by topic with their details
    topic_repos = defaultdict(list)

    # Populate the dictionary with repo details
    for topic, repos in topic_lists.items():
        for repo_url in repos:
            if repo_url in repos_data:
                stars = repos_data[repo_url]["stars"]
                license_info = repos_data[repo_url]["license"]
                all_topics = repos_data[repo_url]["topics"]
                # Exclude the current topic from additional topics
                additional_topics = [t for t in all_topics if t != topic]
                topic_repos[topic].append({
                    "url": repo_url,
                    "stars": stars,
                    "license": license_info,
                    "additional_topics": additional_topics
                })

    # Sort and print repos for each topic
    for topic, repos in topic_repos.items():
        print(f"\nTopic: {topic}")
        print("-" * 50)
        # Sort by stars in descending order
        sorted_repos = sorted(repos, key=lambda x: x["stars"], reverse=True)
        
        for repo in sorted_repos:
            url = repo["url"]
            stars = repo["stars"]
            license_info = repo["license"]
            additional_topics = ", ".join(repo["additional_topics"]) if repo["additional_topics"] else "None"
            print(f"{stars} {url} - License: {license_info} - Additional Topics: {additional_topics}")

    # Handle topics with no matching repo data
    for topic in topic_lists.keys():
        if topic not in topic_repos:
            print(f"\nTopic: {topic}")
            print("-" * 50)
            print("No matching repository data found.")

# Run the script
if __name__ == "__main__":
    topic_lists_file = "topic_lists.txt"
    repo_data_file = "fortran_repo_data.txt"
    process_and_sort_repos(topic_lists_file, repo_data_file)
    