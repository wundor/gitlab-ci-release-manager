#!/usr/local/bin/python
import semver
import os
import argparse
import sys
import requests
import json
import re


class GitLab:
    url = ""
    default_branch = ""
    header = ""
    current_version = ""

    def __init__(self, project_id, server_host, default_branch, token):
        self.url = f"https://{server_host}/api/v4/projects/{project_id}"
        self.default_branch = default_branch
        self.header = {"Private-Token": token}

    def get_latest_MR(self):
        r = requests.get(
            f"{self.url}/repository/commits/{self.default_branch}", headers=self.header
        )
        responce = json.loads(r.text)["message"]
        mr_id = responce[responce.rindex("!") + 1:]
        if re.match(r"^\d+$", mr_id):
            print(f"Found MR id {mr_id}")
        else:
            sys.exit(
                f"ERROR: last commit message does not contains MR number. Got this: {mr_id}"
            )
        return mr_id

    def get_current_version(self):
        r = requests.get(f"{self.url}/repository/tags", headers=self.header)
        version = json.loads(r.text)[0]["name"]
        print(f"Got current version {version}")
        if semver.VersionInfo.isvalid(version):
            print("Version is valid")
        else:
            sys.exit(
                f"ERROR: Current version is not valid! Got this: {version}")
        self.current_version = semver.VersionInfo.parse(version)
        return semver.VersionInfo.parse(version)

    def set_new_version(self, new_version):
        params = {
            "tag_name": str(new_version),
            "ref": self.default_branch,
            "message": str(new_version),
        }
        r = requests.post(
            f"{self.url}/repository/tags", headers=self.header, params=params
        )
        if r.status_code == 201 and json.loads(r.text)["name"] == str(new_version):
            print(f"New version was successfully bumped to {new_version}")
        else:
            print(r.status_code)
            print(r.text)
            sys.exit(f"ERROR: New version was not applied!")

    def get_mr_labels(self, id):
        r = requests.get(f"{self.url}/merge_requests/{id}",
                         headers=self.header)
        labels = json.loads(r.text)["labels"]
        print(f"Got labels: {labels}")
        return labels


def determine_new_version(gitlab, labels):
    if "major" in labels:
        return gitlab.current_version.bump_major()
    elif "feature" in labels:
        return gitlab.current_version.bump_minor()
    elif "bug" in labels:
        return gitlab.current_version.bump_patch()
    else:
        return False


def main(args=None):
    gitlab = GitLab(project_id=args.project, server_host=args.server,
                    default_branch=args.branch, token=args.token)
    mr_id = gitlab.get_latest_MR()
    gitlab.get_current_version()
    labels = gitlab.get_mr_labels(id=mr_id)
    version_bumped = determine_new_version(gitlab=gitlab, labels=labels)
    if version_bumped:
        print(f"New version is {version_bumped}")
        gitlab.set_new_version(new_version=version_bumped)
    else:
        print("No need to bump version, keeping the old one")


if __name__ == "__main__":
    # You can set this if you're running locally
    # os.environ["CI_PROJECT_ID"] = "123"
    # os.environ["CI_SERVER_HOST"] = "gitlab.example.com"
    # os.environ["CI_DEFAULT_BRANCH"] = "main"
    # os.environ["TOKEN"] = "token"
    parser = argparse.ArgumentParser(description="Release manager script")
    parser.add_argument(
        "--project",
        default=os.environ["CI_PROJECT_ID"] if "CI_PROJECT_ID" in os.environ else "",
        help="Set project ID",
    )
    parser.add_argument(
        "--server",
        default=os.environ["CI_SERVER_HOST"] if "CI_SERVER_HOST" in os.environ else "",
        help="Set GitLab server host",
    )
    parser.add_argument(
        "--branch",
        default=os.environ["CI_DEFAULT_BRANCH"] if "CI_DEFAULT_BRANCH" in os.environ else "",
        help="Set GitLab default branch",
    )
    parser.add_argument(
        "--token",
        default=os.environ["TOKEN"] if "TOKEN" in os.environ else "",
        help="Set token",
    )
    args = parser.parse_args()
    if args.project == "":
        sys.exit("Please use CI_PROJECT_ID env or use --project flag")
    if args.server == "":
        sys.exit("Please use CI_SERVER_HOST env or use --server flag")
    if args.branch == "":
        sys.exit("Please use CI_DEFAULT_BRANCH env or use --branch flag")
    if args.token == "":
        sys.exit("Please use TOKEN env or use --token flag")
    main(args)
    # TODO: add arguments for different stuff
    # parser.add_argument(
    #     "--release",
    #     help="TODO: This will create new release branch and all that stuff",
    # )
    # parser.add_argument(
    #     "--major",
    #     action="store_true",
    #     help="This will bump current MAJOR project version",
    # )
    # parser.add_argument(
    #     "--minor",
    #     action="store_true",
    #     help="This will bump current MINOR project version",
    # )
    # parser.add_argument(
    #     "--patch",
    #     action="store_true",
    #     help="This will bump current PATCH project version",
    # )
