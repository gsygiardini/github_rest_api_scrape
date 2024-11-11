import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from repos_module import Repos

class PrintRedirector:
    # We created a custom class to output the prints to the GUI
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END) #Scrolling to the end of the terminal in the GUI
        self.text_widget.update_idletasks() #Constant update command

    def flush(self):  # Required for compatibility with Python's print system
        pass


class GitHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Data Collection System")
        
        self.default_owner = "ibm-developer-skills-network"
        self.default_repo = "xzceb-flask_eng_fr"

        self.max_pull_requests = tk.IntVar(value=25)
        self.repos = Repos()

        self.setup_layout()

    def setup_layout(self):
        # We created a sidebar for a "main menu"
        sidebar = ttk.Frame(self.root, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Main content area
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add buttons to the sidebar
        ttk.Button(sidebar, text="Collect Data for a Repository", command=self.collect_repo_data).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Show All Collected Repositories", command=self.show_repositories_menu).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Generate Visualizations for All Repositories", command=self.create_all_repos_visualizations).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Calculate User Data Correlations", command=self.calculate_user_correlations).pack(fill=tk.X, pady=5)

        ttk.Button(sidebar, text="Print Repo Info", command=self.print_repo_info).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Save User Data", command=self.save_user_data).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Save Pull Request Data", command=self.save_pull_requests_data).pack(fill=tk.X, pady=5)
        ttk.Button(sidebar, text="Save Repository Data", command=self.save_repository_data).pack(fill=tk.X, pady=5)

        ttk.Label(sidebar, text="Max Pull Requests:").pack(pady=5)
        max_pr_spinbox = ttk.Spinbox(sidebar, from_=1, to=100, textvariable=self.max_pull_requests)
        max_pr_spinbox.pack(fill=tk.X, pady=5)

        #Terminal window for the output of information from the program
        self.output_box = tk.Text(self.root, wrap='word', bg='black', fg='white', height=10)
        self.output_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        sys.stdout = PrintRedirector(self.output_box)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def collect_repo_data(self):
        self.clear_content_frame() #Clears previous contents from the frame

        #Box for selecting the owner for the Repo
        ttk.Label(self.content_frame, text="Owner:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        owner_entry = ttk.Entry(self.content_frame)
        owner_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        owner_entry.insert(0, self.default_owner)

        #Box for selecting the Repo
        ttk.Label(self.content_frame, text="Repository:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        repo_entry = ttk.Entry(self.content_frame)
        repo_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        repo_entry.insert(0, self.default_repo)

        # GitHub login token for increased pulls
        TOKEN = ""

        def start_collection():
            owner = owner_entry.get()
            repo = repo_entry.get()

            if owner and repo:
                self.repos.add_repo(url=f"https://github.com/{owner}/{repo}", token=TOKEN,max_pulls=self.max_pull_requests.get())
                print(self.repos.repositories)

                self.repos.repositories[repo].fetch_pull_requests()
                messagebox.showinfo("Success", f"Data collected for {owner}/{repo}")
            else:
                messagebox.showerror("Error", "Please enter both owner and repository names.")

        ttk.Button(self.content_frame, text="Collect Data", command=start_collection).grid(row=2, column=0, columnspan=2, pady=10)

    def show_repositories_menu(self):
        self.clear_content_frame() #Clears previous contents from the frame

        # Display collected repositories in the right content area
        for idx, repo_name in enumerate(self.repos.repositories.keys()):
            ttk.Label(self.content_frame, text=repo_name).grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)

            ttk.Button(self.content_frame, text="Show Summary", command=lambda r=repo_name: self.show_repo_summary(r)).grid(row=idx, column=1, padx=5, pady=5)
            ttk.Button(self.content_frame, text="Show Pull Requests", command=lambda r=repo_name: self.show_pull_requests(r)).grid(row=idx, column=2, padx=5, pady=5)
            ttk.Button(self.content_frame, text="Generate Visuals", command=lambda r=repo_name: self.create_repo_visualizations(r)).grid(row=idx, column=3, padx=5, pady=5)
            ttk.Button(self.content_frame, text="Calculate Correlations", command=lambda r=repo_name: self.calculate_repo_correlations(r)).grid(row=idx, column=4, padx=5, pady=5)

    def show_repo_summary(self, repo_name):
        self.clear_content_frame()

        repo = self.repos.repositories[repo_name]

        open_pulls = repo.open_issues
        closed_pulls = repo.n_of_pulls - repo.open_issues # API does not have closed pulls so we make closed_pulls = total_pulls - open_pulls
        num_users = len(repo.authors.authors)
        oldest_pull_date = min((datetime.strptime(pull.created_at, "%Y-%m-%dT%H:%M:%SZ") for pull in repo.pulls.requests.values()), default="N/A")

        summary_text = (
            f"Number of open pull requests: {open_pulls}\n"
            f"Number of closed pull requests: {closed_pulls}\n"
            f"Number of unique users (Consiring first page only...): {num_users}\n"
            f"Date of the oldest pull request: {oldest_pull_date}"
        )

        ttk.Label(self.content_frame, text=summary_text, justify=tk.LEFT).pack(padx=10, pady=10)

    def show_pull_requests(self, repo_name):
        self.clear_content_frame() #Clears previous contents from the frame

        # Display the pulls in numerical sequence from last to first
        repo = self.repos.repositories[repo_name]
        for idx, pull in enumerate(repo.pulls.requests.values()):
            ttk.Label(self.content_frame, text=f"{pull.title} (#{pull.number})").grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)

    def create_repo_visualizations(self, repo_name):
        repo = self.repos.repositories[repo_name]
        df = pd.DataFrame([{
            "state": pull.state,
            "commits": pull.commits,
            "additions": pull.additions,
            "deletions": pull.deletions,
            "changed_files": pull.changed_files,
            "author_association": pull.user.get("author_association", "None")
        } for pull in repo.pulls.requests.values()])

        # Boxplot: Closed vs Open Pull Requests (Commits)
        plt.figure()
        df.boxplot(column="commits", by="state")
        plt.title("Commits by Pull Request State")
        plt.savefig(f"{repo_name}_commits_boxplot.png")

        # Boxplot: Additions and Deletions by State
        plt.figure()
        df.boxplot(column=["additions", "deletions"], by="state")
        plt.title("Additions and Deletions by Pull Request State")
        plt.savefig(f"{repo_name}_add_del_boxplot.png")

        # Boxplot: Changed Files by Author Association
        plt.figure()
        df.boxplot(column="changed_files", by="author_association")
        plt.title("Changed Files by Author Association")
        plt.savefig(f"{repo_name}_changed_files_boxplot.png")

        # Scatterplot: Additions vs Deletions
        plt.figure()
        plt.scatter(df["additions"], df["deletions"])
        plt.xlabel("Additions")
        plt.ylabel("Deletions")
        plt.title("Additions vs. Deletions Scatterplot")
        plt.savefig(f"{repo_name}_add_vs_del_scatter.png")
        plt.close('all')

        messagebox.showinfo("Visualizations Created", f"Visualizations for {repo_name} saved.")

    def calculate_repo_correlations(self, repo_name):
        self.clear_content_frame()

        repo = self.repos.repositories[repo_name]
        df = pd.DataFrame([{
            "commits": pull.commits,
            "additions": pull.additions,
            "deletions": pull.deletions,
            "changed_files": pull.changed_files
        } for pull in repo.pulls.requests.values()])

        correlation = df.corr()
        ttk.Label(self.content_frame, text=correlation.to_string()).pack(pady=10)

    def print_repo_info(self):
        self.clear_content_frame() #Clears previous contents from the frame
    
        # Define a callback function to handle the repository name after submission
        # i.e. (After I click the button I can click it again, so the function keeps on running in a loop instead of 
        # returning a value and closing. Before using this, the program would close if we clicked the button multiple times.)
        def on_repo_submit(repo_name):
            if repo_name:
                # Call print_repo_info from Repos class
                self.repos.print_repo_info(name=repo_name)
            else:
                print("No repository name provided.")
    
        # Get repository name from user with a callback to continue the process
        self.get_repo_name_from_user(on_submit_callback=on_repo_submit)

    def save_user_data(self):
        self.clear_content_frame()
        
        # Define a callback function to handle user input once submitted (same for previous function)
        def on_user_submit(user_name):
            print(f"This is the user: {user_name}")
            if user_name:
                self.repos.save_user_data(user=user_name)
        
        # Call get_user and pass the callback function
        self.get_user(on_submit_callback=on_user_submit)
        
    def save_pull_requests_data(self):
        self.clear_content_frame() # Clear the content frame and define the callback function
    
        # Define a callback function to handle the repository name after submission
        def on_repo_submit(repo_name):
            if repo_name in self.repos.repositories:
                # Call save_pull_requests_data from Repos class
                self.repos.save_pull_requests_data(repo=self.repos.repositories[repo_name])
                print(f"Pull requests data saved for repository: {repo_name}")
            else:
                print(f"No repository named {repo_name} found in the database.")
    
        # Get repository name from user with a callback to continue the process
        self.get_repo_name_from_user(on_submit_callback=on_repo_submit)

    def save_repository_data(self):
        self.clear_content_frame()# Clear the content frame and define the callback function
        
        def on_repo_submit(repo_name):
            # Proceed with saving once the repo name is obtained
            repo = self.repos.repositories.get(repo_name)
            
            if repo:
                file_path = "repositories.csv"
                
                # No repetition condition for the CSV file...
                # Check if the file exists, load it, or create a new DataFrame
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
            else:
                print(f"No repository named {repo_name} found in the database.")
    
        # Get repository name from user with a callback to continue the process
        self.get_repo_name_from_user(on_submit_callback=on_repo_submit)

    def get_repo_name_from_user(self, on_submit_callback=None):
        self.repo_name = ""  # Clear any previous repository name
    
        # Clear any existing content in the content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
        # Collect all unique repository names
        existing_repo_names = list(self.repos.repositories.keys())
    
        # Create a frame for entering the repository name
        name_entry_frame = ttk.Frame(self.content_frame)
        name_entry_frame.pack(pady=10)
    
        # Label for the repository input
        ttk.Label(name_entry_frame, text="Select or Enter Repository Name:").grid(row=0, column=0)
    
        # Dropdown bar that shows all of the already collected repositories (Combobox)
        repo_name_combobox = ttk.Combobox(name_entry_frame, values=existing_repo_names, width=25)
        repo_name_combobox.grid(row=0, column=1, padx=5)
        repo_name_combobox.set("Select or enter repository")  # Placeholder text
    
        def submit_name():
            # Capture the selected or entered repository name
            self.repo_name = repo_name_combobox.get()
            print(f"Repository name submitted: {self.repo_name}")
    
            # Call the callback function with the repository name if provided
            if on_submit_callback:
                on_submit_callback(self.repo_name)
    
        # Create a Submit button
        submit_button = ttk.Button(name_entry_frame, text="Submit", command=submit_name)
        submit_button.grid(row=0, column=2, padx=5)

    def get_user(self, on_submit_callback=None):
        # Clear any existing content in the content_frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
        # Collect all unique user names from repositories
        existing_users = set()
        for repo in self.repos.repositories.values():
            for auths in repo.authors.authors.values():
                existing_users.add(auths.name)  # Assuming `user_name` is the attribute for username
    
        # Convert the set to a sorted list for the dropdown
        existing_users = sorted(existing_users)
    
        # Create a frame for the dropdown and input
        name_entry_frame = ttk.Frame(self.content_frame)
        name_entry_frame.pack(pady=10)
    
        # Label for the user input
        ttk.Label(name_entry_frame, text="Select or Enter User Name:").grid(row=0, column=0)
    
        # Dropdown bar that shows all of the already collected users (Combobox)
        user_name_combobox = ttk.Combobox(name_entry_frame, values=existing_users, width=25)
        user_name_combobox.grid(row=0, column=1, padx=5)
        user_name_combobox.set("Select or enter user")  # Placeholder text
    
        def submit_name():
            # Capture the selected or entered user name
            self.user_name = user_name_combobox.get()
            print(f"User name submitted: {self.user_name}")
    
            # Call the callback function with the user name if provided
            if on_submit_callback:
                on_submit_callback(self.user_name)
    
        # Create a Submit button
        submit_button = ttk.Button(name_entry_frame, text="Submit", command=submit_name)
        submit_button.grid(row=0, column=2, padx=5)


    # Still needs work. I already created a value that stores the number of pulls per day in the class Repositories.
    # we just need to change this function to plot the results
    def create_all_repos_visualizations(self):
        self.clear_content_frame() 
        ttk.Label(self.content_frame, text="Feature in Progress: Visualizations for all repositories.").pack(pady=10)


        # for repo in self.repos.repositories:
        

        #     df = pd.DataFrame([{
        #         "state": pull.state,
        #         "commits": pull.commits,
        #         "additions": pull.additions,
        #         "deletions": pull.deletions,
        #         "changed_files": pull.changed_files,
        #         "author_association": pull.user.get("author_association", "None")
        #     } for pull in repo.pulls.requests.values()])
    
        #     plt.figure()
        #     df.boxplot(column="commits", by="state")
        #     plt.title("Commits by Pull Request State")
        #     plt.savefig(f"{repo_name}_commits_boxplot.png")
    
        #     plt.figure()
        #     df.boxplot(column=["additions", "deletions"], by="state")
        #     plt.title("Additions and Deletions by Pull Request State")
        #     plt.savefig(f"{repo_name}_add_del_boxplot.png")
    
        #     plt.figure()
        #     df.boxplot(column="changed_files", by="author_association")
        #     plt.title("Changed Files by Author Association")
        #     plt.savefig(f"{repo_name}_changed_files_boxplot.png")
    
        #     plt.figure()
        #     plt.scatter(df["additions"], df["deletions"])
        #     plt.xlabel("Additions")
        #     plt.ylabel("Deletions")
        #     plt.title("Additions vs. Deletions Scatterplot")
        #     plt.savefig(f"{repo_name}_add_vs_del_scatter.png")
        #     plt.close('all')
    
        # messagebox.showinfo("Visualizations for all repos created...")

    def calculate_user_correlations(self):
        self.clear_content_frame()

        # if not self.repos.authors.authors:
        #     ttk.Label(self.content_frame, text="No author data available.").pack(pady=10)
        #     return

        ttk.Label(self.content_frame, text="Feature in Progress: User data correlations.").pack(pady=10)

        data = {
            "name": [],
            "repositories": [],
            "followers": [],
            "following": [],
            "contributions": []
        }

        for author_name, author in self.repos.authors.authors.items():
            data["name"].append(author.name)
            data["repositories"].append(author.repositories)
            data["followers"].append(author.followers)
            data["following"].append(author.following)
            data["contributions"].append(author.contributions)

        df = pd.DataFrame(data)

        stats = df[["repositories", "followers", "following", "contributions"]].describe()
        correlations = df[["repositories", "followers", "following", "contributions"]].corr()

        stats_label = ttk.Label(self.content_frame, text="User Statistics:")
        stats_label.pack(pady=5)

        stats_text = tk.Text(self.content_frame, wrap="word", width=80, height=10)
        stats_text.insert(tk.END, stats.to_string())
        stats_text.config(state="disabled")  # Make the text read-only
        stats_text.pack(pady=5)

        correlation_label = ttk.Label(self.content_frame, text="User Correlations:")
        correlation_label.pack(pady=5)

        correlation_text = tk.Text(self.content_frame, wrap="word", width=80, height=8)
        correlation_text.insert(tk.END, correlations.to_string())
        correlation_text.config(state="disabled")  # Make the text read-only
        correlation_text.pack(pady=5)

        print("User statistics:")
        print(stats)
        print("\nUser correlations:")
        print(correlations)


if __name__ == "__main__":
    root = tk.Tk()

    root.geometry("800x600")  # Set initial window size (width x height)
    root.minsize(1400, 400)    # Set minimum window size to ensure visibility

    app = GitHubApp(root)
    root.mainloop()
