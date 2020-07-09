# Gitlab-CI version manager

Simple script which allows you to bump up version of your project based on GitLab MR labels. Versions are bumped as git tags, so it's language-agnostic in terms of the project language.

Versions are created via [semver structure](https://semver.org/) and these MR labels are supported:  
- **major** - set this if you need to bump MAJOR version of your project (x.0.0)  
- **feature** - set this if you need to bump MINOR version of your project (0.x.0)  
- **bug** - set this ir you need to bump PATCH version of your project (0.0.x)  

I think later I'll add more exotic stuff

**How to integrate it in GitLab-CI**

We have this step in our pipelines:  

```
# Fail MR pipeline if no appropriate labels were set
check-version:
  stage: build
  only:
    - merge_requests
  script:
    - echo $CI_MERGE_REQUEST_LABELS | grep -e 'bug' -e 'chore' -e 'feature' -e 'major'
```

We're looking for these MR labels:  
- **major**: This is a major change that should be thoroughly reviewed. Will bump MAJOR project version  
- **feature**: This is for adding a feature. Will bump MINOR project version  
- **bug**: This is a fix for the bug. Will bump PATCH project version  
- **chore**: Changes to things that don't affect the app code itself. Will not bump project version. Docs, build system, tests and alike  

It was created to run in GitLab-CI environment and it expects these environment variables to function properly:

- CI_PROJECT_ID - Project ID from GitLab. You can find it on the overview page
- CI_SERVER_HOST - GitLab instance URL (without https://)
- CI_DEFAULT_BRANCH - Your trunk branch, on which you need to tag releases
- TOKEN - Your private deploy token (you can create one in your profile -> Settings -> Access Tokens)

It using GitLab API requests. Example URL for GitLab API request:  
`https://gitlab.example.com/api/v4/projects/123/merge_requests/456?private_token=TOKEN`

You can run it in Docker or by itself

**Run script in Docker**

`$ docker build -t glci:volatile .`  
Create `.env` file with appropriate values (or you can just provide environment variables to Docker with `-e` flags)  
`$ docker run --env-file .env glci:volatile`

**Run script by itself**

`$ pip install -r requirements.txt`  
Change `release.py` to provide needed environment variables (or just provide variables in launch time)  
`$ python release.py`

## Release process

Create release branch  
curl -X POST --header "PRIVATE-TOKEN: token" "https://gitlab.example.com/api/v4/projects/123/repository/branches?branch=release-30&ref=develop"

Commit to branch  
curl --request POST \
     --form "branch=release-30" \
     --form "commit_message=Release 30 is here" \
     --form "actions[][action]=create" \
     --form "actions[][file_path]=version" \
     --form "actions[][content]=release-30" \
     --header "PRIVATE-TOKEN: Mwq6NSLebncasAAa_Zq6" \
     "https://gitlab.example.com/api/v4/projects/123/repository/commits"
