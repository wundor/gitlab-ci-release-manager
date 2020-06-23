# Gitlab-CI version manager

Simple script which allows you to bump up version of your project based on GitLab MR labels. Versions are bumped as git tags, so it's language-agnostic in terms of the project language.

It was created to run in GitLab-CI environment and it expects these environment variables to function properly:

- CI_PROJECT_ID - Project ID from GitLab. You can find it on the overview page
- CI_SERVER_HOST - GitLab instance URL (without https://)
- CI_DEFAULT_BRANCH - Your trunk branch, on which you need to tag releases
- TOKEN - Your private deploy token (you can create one in your profile -> Settings -> Access Tokens)

It using GitLab API requests. Example URL for GitLab API request:  
`https://gitlab.example.com/api/v4/projects/123/merge_requests/456?private_token=TOKEN`

You can run it in Docker or by itself with Nodejs

**Run script in Docker**

`$ docker build -t glci:volatile .`  
Create `.env` file with appropriate values (or you can just provide environment variables to Docker with `-e` flags)  
`$ docker run --env-file .env glci:volatile`


**Run script by itself**

`$ npm ci`  
Change `index.js` to provide needed environment variables (or just provide variables to Node in launch time)  
`$ node index.js`
