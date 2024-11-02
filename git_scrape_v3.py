import requests
from datetime import datetime
from bs4 import BeautifulSoup

class Owner:
    def __init__(self, login="", **kwargs):
        self.login = login
        self.kwargs = kwargs

    def __repr__(self):
        return f"Owner(login={self.login})"

class License:
    def __init__(self, key="", name="", spdx_id="", url="", node_id="" , **kwargs):
        self.key = key
        self.name = name
        self.spdx_id = spdx_id
        self.url = url
        self.node_id = node_id
        self.kwargs = kwargs

    def __repr__(self):
        return f"License(name='{self.name}, key={self.key}')"

# class PullRequest:
#     def __init__():

# class PullRequests:
#     def __init__():

class GitHubRepository:
    def __init__(self, url="", token="", **kwargs):
        self.url = url
        self.api_url = self.convert_to_api_url(url)
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else None,
            "Accept": "application/vnd.github.v3+json"
        }
        self.date_of_collection = ""
        self.kwargs = kwargs

        
        # Fetch and store the repository data
        self.fetch_repo_data()

    def convert_to_api_url(self, github_url):
        # Me take github link and me put res api 
        api_url = github_url.replace("https://github.com/", "https://api.github.com/repos/")
        return api_url

    def fetch_repo_data(self):
        # Me download data from git link that me assign to url
        response = requests.get(self.api_url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Because me no want big class in __init__, me use dynamic key setting
            for key, value in data.items():
                if key=="license":
                    value = License(**value)
                if key=="owner":
                    value = Owner(**value)

                setattr(self, key, value)

            setattr(self, "date_of_collection", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            print(f"Error status code, impossible to access page ಠ_ಠ: {response.status_code}")
            self.error = response.status_code

    def fetch_pull_requests(self):
        #Me has download pull request page, but me no know what to download from there
        response = requests.get(self.api_url, headers=self.headers)


    def __repr__(self):
        # Me create function to print important stuff
        return f"<{self.owner}>/<{self.name}>: <{self.description}> (<self.watchers>)"

        # return (f"<GitHubRepository(name='{self.name}', full_name='{self.full_name}', "
                # f"private={self.private}, description='{self.description}', forks={self.forks})>")


class Repos:
    def __init__(self):
        self.repositories = {}

    def add_repo(self, url="", token="", **kwargs):
        repo = GitHubRepository(url, token)

        if isinstance(repo, GitHubRepository):
            if repo.name not in self.repositories:
                self.repositories[repo.name] = repo
            else:
                print("Repository already existent in the database: (ㆆᴗㆆ)")
            
        else:
            raise TypeError("Only instances of GitHub repositories may be added to the Scraper class ┐( ˘_˘)┌ ...")

    def print_repo(self, name=""): 
        if name=="" or name==None:
            print("Please, enter a valid name for the repository you want to print... ⊙▂⊙")
            # raise TypeError("Please, enter a valid name for the repository you want to print... ⊙▂⊙")

        if name in self.repositories:
            repo = self.repositories[name]    
            print(repo)
        else:
            print(f"No repository named {name}. ヾ(oﾟДﾟ)ﾉ")

    def print_repo_info(self, name=""):
        if name=="" or name==None:
            print("Please, enter a valid name for the repository you want to print... ⊙▂⊙")

        if name in self.repositories:
            repo = self.repositories[name]    
            print("------------------------------------------------------------//------------------------------------------------------------")
            print(f"owner={repo.owner}")
            print(f"description={repo.description}")
            print(f"homepage={repo.url}")
            print(f"license={repo.license}")
            print(f"# of forks={repo.forks}")
            print(f"# of watchers={repo.watchers}")
            print(f"date of collection={repo.date_of_collection}")
            print("------------------------------------------------------------//------------------------------------------------------------")
        else:
            print(f"No repository named {name}. ヾ(oﾟДﾟ)ﾉ")





# # Create an instance of the GitHubRepository class
# repo_data = {
#     "description": "A sample repository",
#     "homepage": "https://github.com/my-username/my-repo",
#     "license": "MIT License",
#     "forks": 10,
#     "date_of_collection": "2023-11-06"
# }

# my_repo = GitHubRepository(**repo_data)

repos = Repos()
repos.add_repo(url="https://github.com/ibm-developer-skills-network/xzceb-flask_eng_fr",token="")

# repos.print_repo_info("xzceb-flask_eng_fr")




# repos.print_repo("xzceb-flask_eng_fr")



# Access attributes of the repository object
# print(my_repo.forks)  # Output: 10
# print(my_repo.license)  # Output: "MIT License"
