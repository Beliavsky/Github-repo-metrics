""" process repo data obtained by running xrepo_data.py,
listing the most common topics """
from github_util import read_repo_data, topics_to_repos
from util import sort_dict_by_value_length

nrepos_min = 1
max_repos_print = 100
print_dd = False
infile = "fortran_repo_data.txt" # output of xrepo_data.py
print_repo_names = True
dd = read_repo_data(infile)
if print_dd:
    for key, value in dd.items():
        print("\n" + key)
        print(value)
dtopics = sort_dict_by_value_length(topics_to_repos(dd))
for key, value in dtopics.items():
    nrepos = len(value)
    if nrepos < nrepos_min:
        break
    print("%5d"%nrepos, key)
    if print_repo_names and len(value) <= max_repos_print:
        for x in value:
            print(x)
        print()


        