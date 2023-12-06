import os
import re


class Commit:
    type = ""
    branch_name = ""
    branch_from = ""
    merge_from = ""
    message = ""
    commit_id = ""
    last_commit_id = ""

    def __init__(self, commit_id, message, type_c, last_commit_id=None, branch_from=None, merge_from=None):
        self.type = type_c
        self.commit_id = commit_id
        self.message = message
        if last_commit_id is not None:
            self.last_commit_id = last_commit_id
        if branch_from is not None:
            self.branch_from = branch_from
        if merge_from is not None:
            self.merge_from = merge_from


class Branch:
    name = ""
    commits = []

    def __init__(self, name):
        self.name = name
        self.commits = []

    def add_commit(self, commit: Commit):
        commit.branch_name = self.name
        self.commits.append(commit)


class GitDataProcess:
    branches = []

    def add_branch(self, branch):
        self.branches.append(branch)

    def make_tree(self):
        tb = TreeBuilder()
        for branch in self.branches:
            for commit in branch.commits:
                if commit.type == "init" or commit.type == "branch" or commit.type == "merge":
                    continue
                elif commit.type == "commit":
                    for branch_c in self.branches:
                        for commit_c in branch_c.commits:
                            if commit_c.commit_id == commit.last_commit_id:
                                if not (commit_c.branch_name == commit.branch_name) and commit_c.type == "branch":
                                    continue
                                last_commit = commit_c
                                tb.add_node(last_commit, commit)
                                break
                else:
                    print(f"error: commit type {commit.type} not found")
        tb.print_tree()


class TreeBuilder:
    nodes = []

    def add_node(self, parent, new):
        temp = [parent, new]
        self.nodes.append(temp)

    def print_tree(self):
        print("digraph G {")
        for node in self.nodes:
            temp = "\"Ветка: "
            temp += node[0].branch_name + ", Коммит: "
            temp += node[0].message

            temp += "\" -> \"Ветка: "

            temp += node[1].branch_name + ", Коммит: "
            temp += node[1].message
            temp += "\""
            print(temp)
        print("}")


def readFiles(path):
    gd = GitDataProcess()
    path_commits = path.replace("\\", "/") + ".git/logs/refs/heads"
    for filename in os.listdir(path_commits):
        with open(os.path.join(path_commits, filename), "r", encoding="utf-8") as file:
            branch = Branch(filename)
            for line in file:
                commit_info = line.split()
                last_commit_id = commit_info[0]
                current_commit_id = commit_info[1]
                commit_message_match = re.search(r": (.+)", line)
                commit_message = commit_message_match.group(1)
                commit = None
                if "commit (initial)" in line:
                    commit = Commit(current_commit_id, commit_message, "init")
                elif "commit" in line:
                    commit = Commit(current_commit_id, commit_message, "commit", last_commit_id=last_commit_id)
                elif "merge" in line:
                    merge_name_match = re.search(r"merge (.+)", line)
                    merge_name = merge_name_match.group(1)
                    commit = Commit(current_commit_id, commit_message, "merge", last_commit_id=last_commit_id, merge_from=merge_name)
                elif "branch: Created from" in line:
                    branch_name_match = re.search(r"branch: Created from (.+)", line)
                    branch_name = branch_name_match.group(1)
                    commit = Commit(current_commit_id, commit_message, "branch", last_commit_id=last_commit_id, branch_from=branch_name)
                if commit is not None:
                    branch.add_commit(commit)
                else:
                    print(f"Error reading commit: {line}")
            gd.add_branch(branch)
    return gd


if __name__ == "__main__":
    # test_path = str(input("Введите путь к локальному репозиторию -> "))
    path = ""

    process = readFiles(path)
    process.make_tree()


#$oigarhgioashryg0
#branch0