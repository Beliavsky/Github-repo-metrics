""" for a set of GitHub URLs, scrape data for the repos and print it """
from github_util import repo_data

max_repos = None
infile = "github_fortran_urls.txt"
lines = open(infile, "r").readlines()[:max_repos]
for line in lines:
    repo_url = line.strip()
    print("\n" + repo_url)
    dd = repo_data(repo_url)
    for key, value in dd.items():
        print(key, value)
