#!/usr/bin/env bash

set +e
pr_info="$(gh pr list -l dependencies --search 'review:approved' --limit 1 | grep 'dependabot')"
# shellcheck disable=SC2028
#echo "[DEBUG] PR info: \n $pr_info"
pr_exist="$?"
if [ "$pr_exist" == "1" ];
then
    echo "PR has been merged. Stop this CI workflow."
    # Save the value to environment variable in GitHub Action
#    echo "PR_EXIST=$pr_exist" >> $GITHUB_OUTPUT
    exit 0
else
    pr_number="$(echo "$pr_info" | cut -d ' ' -f 1 | tr -d -c 0-9)"
    # Save the value to environment variable in GitHub Action
#    echo "PR_NUMBER=$pr_number" >> $GITHUB_OUTPUT
    # shellcheck disable=SC2059
    printf "$pr_number"
    exit 0
fi
