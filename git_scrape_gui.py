import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from repos_module import Repos


class GitHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Data Collection System")
        self.setup_main_menu()

        # Assuming Repos is a pre-existing class managing repositories
        self.repos = Repos()

    def setup_main_menu(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="GitHub Data Collection System", font=("Arial", 14)).grid(row=0, column=0, columnspan=2)

        ttk.Button(main_frame, text="Collect Data for a Repository", command=self.collect_repo_data).grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        ttk.Button(main_frame, text="Show All Collected Repositories", command=self.show_repositories_menu).grid(row=2, column=0, sticky=tk.W+tk.E, pady=5)
        ttk.Button(main_frame, text="Generate Visualizations for All Repositories", command=self.create_all_repos_visualizations).grid(row=3, column=0, sticky=tk.W+tk.E, pady=5)
        ttk.Button(main_frame, text="Calculate User Data Correlations", command=self.calculate_user_correlations).grid(row=4, column=0, sticky=tk.W+tk.E, pady=5)

    def collect_repo_data(self):
        collect_window = tk.Toplevel(self.root)
        collect_window.title("Collect Repository Data")

        ttk.Label(collect_window, text="Owner:").grid(row=0, column=0, padx=5, pady=5)
        owner_entry = ttk.Entry(collect_window)
        owner_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(collect_window, text="Repository:").grid(row=1, column=0, padx=5, pady=5)
        repo_entry = ttk.Entry(collect_window)
        repo_entry.grid(row=1, column=1, padx=5, pady=5)

        def start_collection():
            owner = owner_entry.get()
            repo = repo_entry.get()
            if owner and repo:
                self.repos.add_repo(url=f"https://github.com/{owner}/{repo}", token="")
                print(self.repos.repositories)

                self.repos.repositories[repo].fetch_pull_requests()
                messagebox.showinfo("Success", f"Data collected for {owner}/{repo}")
                collect_window.destroy()
            else:
                messagebox.showerror("Error", "Please enter both owner and repository names.")

        ttk.Button(collect_window, text="Collect Data", command=start_collection).grid(row=2, column=0, columnspan=2, pady=10)

    def show_repositories_menu(self):
        repos_window = tk.Toplevel(self.root)
        repos_window.title("Collected Repositories")

        for idx, repo_name in enumerate(self.repos.repositories.keys()):
            ttk.Label(repos_window, text=repo_name).grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)

            ttk.Button(repos_window, text="Show Summary", command=lambda r=repo_name: self.show_repo_summary(r)).grid(row=idx, column=1, padx=5, pady=5)
            ttk.Button(repos_window, text="Show Pull Requests", command=lambda r=repo_name: self.show_pull_requests(r)).grid(row=idx, column=2, padx=5, pady=5)
            ttk.Button(repos_window, text="Generate Visuals", command=lambda r=repo_name: self.create_repo_visualizations(r)).grid(row=idx, column=3, padx=5, pady=5)
            ttk.Button(repos_window, text="Calculate Correlations", command=lambda r=repo_name: self.calculate_repo_correlations(r)).grid(row=idx, column=4, padx=5, pady=5)

    def show_repo_summary(self, repo_name):
        repo = self.repos.repositories[repo_name]
        summary_window = tk.Toplevel(self.root)
        summary_window.title(f"Summary of {repo_name}")

        # Calculating summary details
        open_pulls = sum(1 for pull in repo.pulls.requests.values() if pull.state == 'open')
        closed_pulls = sum(1 for pull in repo.pulls.requests.values() if pull.state == 'closed')
        num_users = len(repo.authors.authors)
        oldest_pull_date = min((datetime.strptime(pull.created_at, "%Y-%m-%dT%H:%M:%SZ") for pull in repo.pulls.requests.values()), default="N/A")

        summary_text = (
            f"Number of open pull requests: {open_pulls}\n"
            f"Number of closed pull requests: {closed_pulls}\n"
            f"Number of unique users: {num_users}\n"
            f"Date of the oldest pull request: {oldest_pull_date}"
        )

        ttk.Label(summary_window, text=summary_text, justify=tk.LEFT).pack(padx=10, pady=10)

    def show_pull_requests(self, repo_name):
        repo = self.repos.repositories[repo_name]
        pull_requests_window = tk.Toplevel(self.root)
        pull_requests_window.title(f"Pull Requests for {repo_name}")

        for idx, pull in enumerate(repo.pulls.requests.values()):
            ttk.Label(pull_requests_window, text=f"{pull.title} (#{pull.number})").grid(row=idx, column=0, sticky=tk.W, padx=5, pady=5)

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
        repo = self.repos.repositories[repo_name]
        df = pd.DataFrame([{
            "commits": pull.commits,
            "additions": pull.additions,
            "deletions": pull.deletions,
            "changed_files": pull.changed_files
        } for pull in repo.pulls.requests.values()])

        correlation = df.corr()
        messagebox.showinfo("Correlation Data", correlation.to_string())

    def create_all_repos_visualizations(self):
        # Aggregate data across all repositories and generate visualizations
        messagebox.showinfo("Feature in Progress", "This feature is under development.")

    def calculate_user_correlations(self):
        # Calculate correlations among user data (followers, following, contributions)
        messagebox.showinfo("Feature in Progress", "This feature is under development.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubApp(root)
    root.mainloop()
