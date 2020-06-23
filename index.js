// Example URL for GitLab API request:
// https://gitlab.example.com/api/v4/projects/123/merge_requests/456?private_token=TOKEN
const http = require('https');
const semver = require('semver')

const projectID = process.env.CI_PROJECT_ID
const serverHost = process.env.CI_SERVER_HOST
const defaultBranch = process.env.CI_DEFAULT_BRANCH
const token = process.env.TOKEN

function httpRequest(options) {
    return new Promise ((resolve, reject) => {
      http.get(options, (res) => {
        res.on("data", function(data) {
          resolve(data);
        });
      }).on('error', function(e) {
        console.log("Got error: " + e.message);
        reject(e);
      });
    }); 
}

async function getMR() {
    let data = await httpRequest({
      hostname: `${serverHost}`,
      path: `/api/v4/projects/${projectID}/repository/commits/${defaultBranch}`,
      headers: {
        'Private-Token': `${token}`
    }})
    let body = JSON.parse(data.toString())
    console.log(`Got commit: ${body.message}`)
    let mrId = body.message.substring(body.message.lastIndexOf("!") + 1);
    if (mrId.match(/^\d+$/g)) {
        console.log(`Found MR id: ${mrId}`)
    } else {
        console.log(`ERROR: last commit message does not contains MR number. Got this: ${mrId}`);
        process.exit(1);
    }
    return mrId;
}

async function getLabels(mergeRequestId) {
    let data = await httpRequest({
        hostname: `${serverHost}`,
        path: `/api/v4/projects/${projectID}/merge_requests/${mergeRequestId}`,
        headers: {
            'Private-Token': `${token}`
        }
    })
    let body = JSON.parse(data.toString())
    let labels = body.labels;
    if (typeof body.labels === 'undefined') {
        console.log('ERROR: No labels on newly created MR! Got this:');
        console.log(body);
        process.exit(1);
    }
    console.log(`Got label(s): ${labels}`)
    return labels
}

async function getCurrentVersion() {
    let data = await httpRequest({
      hostname: `${serverHost}`,
      path: `/api/v4/projects/${projectID}/repository/tags`,
      headers: {
        'Private-Token': `${token}`
      }
    })
    let currentVersion = JSON.parse(data.toString())[0].name;
    console.log(`Got current version: ${currentVersion}`)
    if (semver.valid(currentVersion)) {
      console.log('Version is valid')
    }
    return currentVersion;
}

async function updateProjectVersion(newVersion) {
    let data = await httpRequest({
      hostname: `${serverHost}`,
      path: `/api/v4/projects/${projectID}/repository/tags?tag_name=${newVersion}&ref=${defaultBranch}`,
      method: 'POST',
      headers: {
        'Private-Token': `${token}`
      }
    })
    var expectedVersion = JSON.parse(data.toString()).name;
    if (expectedVersion !== newVersion) {
        console.log(`ERROR: tag was not applied, got this instead: ${data.toString()}`);
        process.exit(1);
    } else {
        console.log(`New version is now ${expectedVersion}`);
    }
    // If you want to play it safe and delete tag afterwards for some reason
    // await httpRequest({
    //   hostname: `${serverHost}`,
    //   path: `/api/v4/projects/${projectID}/repository/tags/${newVersion}`,
    //   method: 'DELETE',
    //   headers: {
    //     'Private-Token': `${token}`
    //   }
    // })
}

(async () => {
    try {
        if (!process.env.CI_PROJECT_ID || !process.env.CI_SERVER_HOST || !process.env.CI_DEFAULT_BRANCH || !process.env.TOKEN) {
          console.log('ERROR: Please specify all needed environment variables: CI_PROJECT_ID CI_SERVER_HOST CI_DEFAULT_BRANCH TOKEN. See README.');
          process.exit(1);
        }
        var currentVersion = await getCurrentVersion();
        var newVersion = currentVersion;
        var mr = await getMR();
        var labels = await getLabels(mr);
        if (labels.includes('major')) {
            newVersion = semver.inc(currentVersion, 'major')
        } else if (labels.includes('feature')) {
            newVersion = semver.inc(currentVersion, 'minor')
        } else if (labels.includes('bug')) {
            newVersion = semver.inc(currentVersion, 'patch')
        }
        if (semver.gt(newVersion, currentVersion)) {
            console.log(`Updating the version from ${currentVersion} to ${newVersion}`);
            await updateProjectVersion(newVersion);
        } else {
            console.log('Keeping the old version');
        }
    } catch (e) {
        console.log(e)
    }
})();
