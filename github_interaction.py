from github import Github

g = Github()

def get_user_repos(username):
	user = g.get_user(username) # target user
	repos = user.get_repos()
	non_forks = []
	for repo in user.get_repos():
	    if repo.fork is False:
	        non_forks.append(repo.name)
	return non_forks
