import requests
import json
import os

GITHUB_USERNAME = "Max-Lee-explore"  # GitHub username
OUTPUT_FILE = "repos.md"
PER_PAGE = 100  # max allowed
CATEGORIES_FILE = "repo_categories.json"

# Default categories if no categories file exists
DEFAULT_CATEGORIES = {
    "Automation with AI": [],
    "RAG": [],
    "NLP": [],
    "Audiovisual": [],
    "Learning Resources": [],
    "Web Development": [],
    "Personal Projects": [],
    "Other": []
}

def load_categories():
    if os.path.exists(CATEGORIES_FILE):
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_CATEGORIES

def save_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2)

def fetch_starred_repos(username):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/starred?per_page={PER_PAGE}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error:", response.status_code, response.json())
            break
        page_data = response.json()
        if not page_data:
            break
        repos.extend(page_data)
        page += 1
    return repos

def categorize_repos(repos, categories):
    # Keep existing categories
    existing_categories = {category: repos_list.copy() for category, repos_list in categories.items()}
    
    # Get all currently categorized repos
    categorized_repos = set()
    for repos_list in existing_categories.values():
        categorized_repos.update(repos_list)
    
    # Add new repos to "Other"
    for repo in repos:
        name = repo["full_name"]
        if name not in categorized_repos:
            existing_categories["Other"].append(name)
    
    return existing_categories

def write_to_markdown(repos, categories):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# ⭐ Starred GitHub Repositories\n\n")
        
        # Write each category
        for category, repos_list in categories.items():
            if repos_list:  # Only show categories that have repos
                f.write(f"## {category}\n\n")
                
                # Write repos in this category
                for repo_name in repos_list:
                    # Find the repo details
                    repo = next((r for r in repos if r["full_name"] == repo_name), None)
                    if repo:
                        name = repo["full_name"]
                        url = repo["html_url"]
                        description = repo["description"] or "No description provided."
                        f.write(f"### [{name}]({url})\n")
                        f.write(f"{description}\n\n")

def main():
    # Load existing categories
    categories = load_categories()
    
    # Fetch starred repos
    starred_repos = fetch_starred_repos(GITHUB_USERNAME)
    
    # Categorize repos
    categories = categorize_repos(starred_repos, categories)
    
    # Save updated categories
    save_categories(categories)
    
    # Write to markdown
    write_to_markdown(starred_repos, categories)
    print(f"✅ {len(starred_repos)} repositories saved to {OUTPUT_FILE}")
    print("\nTo categorize repositories, edit the categories in repo_categories.json")
    print("Available categories:", ", ".join(categories.keys()))

if __name__ == "__main__":
    main()