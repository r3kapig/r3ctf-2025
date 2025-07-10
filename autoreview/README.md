# Auto Review

AI Powered pull request reviews

## Usage
Simply run `auto-review client` in your GitHub Actions workflow, and the PR will automatically be sent to a LLM for review!

Check out [`.github/workflows/auto_review.yml`](.github/workflows/auto_review.yml) for an example workflow.

## Challenge

The flag has been stored in the `FLAG` repo secret. Your job is to exploit vulnerabilities in the GitHub Actions workflow and leak the flag.

To solve this challenge, you will need to fork this repository. You will also need your project ID, which can be found in this repository's description. The project ID is a hash of your GitHub username.

Your project ID is used to track and limit the consumption of LLM tokens. You are limited to 200,000 tokens, which is more than enough to solve this challenge. You can monitor your token consumption by requesting `/project` on the instancer. Should you require more tokens, please contact an admin.

Re-creation of this repository is subject to rate limits. If you run into a "Limit exceeded" error, please contact an admin with your IP address and the link to this repo.

All the code used in this challenge is stored in this repository.
- [`server`](server): This package runs on the Auto Review server and manages interactions with the LLM.
- [`client`](client): This package runs in your GitHub Action workflow and authenticates to the server using the flag and your project ID.
- [`server/gh_instancer`](server/gh_instancer): Code for the instancer you used to create this repo. You will not need to (and should not) find any bugs in this code.
