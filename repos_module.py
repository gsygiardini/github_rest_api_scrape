import os
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By


class Author:
    def __init__(self, **kwargs):
        self.name = kwargs.get("login")
        self.repositories = kwargs.get("public_repos")
        self.followers = kwargs.get("followers")
        self.following = kwargs.get("following")
        self.contributions = kwargs.get("contributions",0)
        self.kwargs = kwargs

    def __repr__(self):
        return f"author=<{self.name}>/#_of_repositories=<{self.repositories}>/#_of_followers=<{self.followers}>/#_of_followings=<{self.following}>/#_of_contributions=<{self.following}>"
                

class Authors:
    def __init__(self):
        self.authors = {}

    def add_author(self, url=""):
        if url==None or url=="":
            print("Please provide a valid link for the author. ( ͡~ ͜ʖ ͡° )")
            return 0
        else:
            response = requests.get(url)
            data = response.json()

            print(f"Found author {data["login"]}")

            self.authors[data["login"]] = Author(**data)

            html_url = self.convert_to_html_url(url)

            response = requests.get(html_url)
            soup = bs(response.text, "html.parser")

            contribution_tag = soup.find_all('h2', class_="f4 mb-2 text-normal")

            # contribution_tag = soup.find('h2', class_="f4 text-normal mb-2")
            # contribution_tag = soup.find(string="contributions in the last year")
            # print(contribution_tag.get_text())

            # self.authors[data["login"]].contributions = 
            
            # print(self.authors[data["login"]])

    def convert_to_html_url(self, url):
        # Me take github link and me put res api 
        html_url = url.replace("https://api.github.com/users/", "https://github.com/")
        return html_url

    # def __repr__(self):
    #     auths = []
    #     for auth in self.authors:
    #         auths.append(auth.name)

    #     return auths

class Owner:
    def __init__(self, login="", **kwargs):
        self.login = login
        self.kwargs = kwargs

    def __repr__(self):
        return f"Owner(login={self.login})"

class License:
    def __init__(self, **kwargs):
        self.url     = kwargs.get("url")
        self.key     = kwargs.get("key")
        self.name    = kwargs.get("name")
        self.node_id = kwargs.get("node_id")
        self.spdx_id = kwargs.get("spdx_id")
        self.kwargs  = kwargs

    def __repr__(self):
        return f"License(name='{self.name}, key={self.key}')"

class PullRequest:
    def __init__(self, **kwargs):
        self.user       = kwargs.get("user")
        self.body       = kwargs.get("body")       
        self.title      = kwargs.get("title")
        self.state      = kwargs.get("state")      
        self.number     = kwargs.get("number")     
        self.commits    = kwargs.get("commits")
        self.additions  = kwargs.get("additions")
        self.deletions  = kwargs.get("deletions")
        self.closed_at  = kwargs.get("closed_at")  
        self.created_at = kwargs.get("created_at")
        self.changed_files = kwargs.get("changed_files ")
        self.kwargs     = kwargs     

        self.author = Author()

    def __repr__(self):
        return f"title={self.title}\n number={self.number}\n state={self.state}\n user={self.user["login"]}"

class PullRequests:
    def __init__(self):
        self.requests = {}
        self.daily_counts = {}

    def __repr__(self):
        num = []

        for i in range(1,len(self.requests)):
            num.append(self.requests[f"{i}"].number)
            
        return f"Total requests: {num}"

    def daily_open_closed_counts(self):
        # Temporary dictionary to count open and closed pull requests by date
        daily_counts = defaultdict(lambda: {"open": 0, "closed": 0})
        for pull in self.requests.values():
            created_date = datetime.strptime(pull.created_at, "%Y-%m-%dT%H:%M:%SZ").date()
            daily_counts[created_date]["open"] += 1

            if pull.state == "closed" and pull.closed_at:
                closed_date = datetime.strptime(pull.closed_at, "%Y-%m-%dT%H:%M:%SZ").date()
                daily_counts[closed_date]["closed"] += 1
        
        self.daily_counts = dict(daily_counts)

        for date, counts in sorted(self.daily_counts.items()):
            print(f"{date}: Open: {counts['open']}, Closed: {counts['closed']}")

class GitHubRepository:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.api_url = self.convert_to_api_url(self.url)
        self.token = kwargs.get("token")
        self.headers = {
            "User-Agent": "request",
            "Authorization": f"token {self.token}" if self.token else None,
            "Accept": "application/vnd.github.v3+json"
        }
        self.date_of_collection = ""

        self.n_of_pulls = 0
        self.open_issues = kwargs.get("open_issues")

        self.max_pulls = kwargs.get("max_pulls",4)

        self.name = ""
        self.forks = ""
        self.owner = ""
        self.license = ""
        self.watchers = ""
        self.description = ""

        self.fetch_repo_data()
        self.pulls = PullRequests()

        self.authors = Authors()
        self.kwargs = kwargs

    def convert_to_api_url(self, github_url):
        # Me take github link and me put res api 
        api_url = github_url.replace("https://github.com/", "https://api.github.com/repos/")
        return api_url

    def fetch_repo_data(self):
        # Me download data from git link that me assign to url
        response = requests.get(self.api_url, headers=self.headers)
        rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        print(f"Remaining API calls {rate_limit_remaining}")

        if rate_limit_remaining == 0:
            reset_time = int(response.headers.get("X-RateLimit-Reset"))
            print("Rate limit exceeded. Try again after:", reset_time)

        if response.status_code == 200:
            data = response.json()
            
            # Because me no want big class in __init__, me use dynamic key setting
            for key, value in data.items():
                if key=="license":
                    if isinstance(value, dict):
                        value = License(**value)
                    else:
                        value = License()
                if key=="owner":
                    if isinstance(value, dict):
                        value = Owner(**value)
                    else:
                        value = Owner()

                if key!="url":
                    setattr(self, key, value)

            setattr(self, "date_of_collection", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        else:
            print(f"Error status code, impossible to access page ಠ_ಠ: {response.status_code}")
            self.error = response.status_code

    def fetch_pull_requests(self):
        #Me has download pull request page, but me no know what to download from there
        response = requests.get(self.api_url+"/pulls", headers=self.headers)
        data = response.json()

        try:
            self.n_of_pulls = int(data[0]["number"])

            n_of_pulls = 0
            if self.max_pulls==None:
                n_of_pulls = self.n_of_pulls
            else:
                n_of_pulls = self.max_pulls
    
            for i in range(1,n_of_pulls+1):
                idx = self.n_of_pulls - i
                response = requests.get(self.api_url+"/pulls/"+f"{idx}", headers=self.headers)
                rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
                print(f"Remaining API calls {rate_limit_remaining}")

                if response.status_code == 200:
                    data = response.json()
                    pull = PullRequest(**data)
    
                    self.authors.add_author(pull.user["url"])

                    self.pulls.requests[f"{idx}"] = pull
        except:
            print(f"No pull request available for repository {self.name}")

        

    def __repr__(self):
        # Me create function to print important stuff
        return f"owner=<{self.owner}>/name=<{self.name}>: description=<{self.description}> (watchers=<{self.watchers}>)"

        # return (f"<GitHubRepository(name='{self.name}', full_name='{self.full_name}', "
                # f"private={self.private}, description='{self.description}', forks={self.forks})>")


class Repos:
    def __init__(self):
        self.repositories = {}

    def add_repo(self, url="", token="", max_pulls=4):
        repo = GitHubRepository(url=url, token=token, max_pulls=max_pulls)

        if isinstance(repo, GitHubRepository):
            print(repo.name)
            if repo.name not in self.repositories:
                self.repositories[repo.name] = repo
            else:
                print("Repository already existent in the database: (ㆆᴗㆆ)")
            
        else:
            raise TypeError("Only instances of GitHub repositories may be added to the Scraper class ┐( ˘_˘)┌ ...")

    def save_repository_data(self, repo):
        #Me assign file path for csv
        file_path = "repositories.csv"
        
        # Me check if me created previous file, if no, me create new if yes me no create
        if os.path.exists(file_path):
            repo_df = pd.read_csv(file_path)
        else:
            repo_df = pd.DataFrame(columns=["name", "description", "watchers", "forks", "license"])

        new_data = []
        if not ((repo_df["name"] == repo.name) & (repo_df["description"] == repo.description)).any():
            new_repo_data = {
                "name": repo.name,
                "description": repo.description,
                "watchers": repo.watchers,
                "forks": repo.forks,
                "license": repo.license.name if repo.license else None
            }
            new_data.append(new_repo_data)
        else:
            print("Repository data already exists in repositories.csv")

        if new_data:
            new_data_df = pd.DataFrame(new_data)
            repo_df = pd.concat([repo_df, new_data_df], ignore_index=True)
    
        repo_df.to_csv(file_path, index=False)
        print(f"Repository data saved to {file_path}")
        

    def save_pull_requests_data(self, repo):
        #Me assign file path for csv
        file_path = f"repos/{repo.owner.login}-{repo.name}.csv"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            pulls_df = pd.read_csv(file_path)
        else:
            pulls_df = pd.DataFrame(columns=["title", "number", "state", "commits", "additions", "deletions", "changed_files"])

        new_data = []
        for pull_id, pull in repo.pulls.requests.items():
            if not (pulls_df["number"] == int(pull.number)).any():
                new_pull_data = {
                    "title": pull.title,
                    "number": pull.number,
                    "state": pull.state,
                    "commits": pull.commits,
                    "additions": pull.additions,
                    "deletions": pull.deletions,
                    "changed_files": pull.changed_files
                }
                new_data.append(new_pull_data)
        
        # Append new data using pd.concat() if there is any new data
        if new_data:
            new_data_df = pd.DataFrame(new_data)
            pulls_df = pd.concat([pulls_df, new_data_df], ignore_index=True)

        pulls_df.to_csv(file_path, index=False)
        print(f"Pull requests data saved to {file_path}")

    def save_user_data(self, user):
        file_path = "users.csv"

        if os.path.exists(file_path):
            users_df = pd.read_csv(file_path)
        else:
            users_df = pd.DataFrame(columns=["name", "public_repos", "followers", "following", "contributions"])

        for name in self.repositories:
            repo = self.repositories[name]

            for author_name, author_instance in repo.authors.authors.items():
                if author_instance.name == user:
                    if not (users_df["name"] == author_instance.name).any():
                        new_user_data = {
                            "name": author_instance.name,
                            "public_repos": author_instance.repositories,
                            "followers": author_instance.followers,
                            "following": author_instance.following,
                            "contributions": author_instance.contributions
                        }
                        
                        new_user_df = pd.DataFrame([new_user_data])
                        users_df = pd.concat([users_df, new_user_df], ignore_index=True)

                        users_df.to_csv(file_path, index=False)

                        print(f"User data saved to {file_path}")
                    else:
                        print(f"User {author_instance.name} data already exists in users.csv")

    def print_repo(self, name=""): 
        if name=="" or name==None:
            print("Please, enter a valid name for the repository you want to print... ⊙▂⊙")
            # raise TypeError("Please, enter a valid name for the repository you want to print... ⊙▂⊙")

        if name in self.repositories:
            repo = self.repositories[name]    
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