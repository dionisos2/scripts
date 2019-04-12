#!/bin/python

from plumbum import cli, local # See https://plumbum.readthedocs.io/en/latest/cli.html
from datetime import date, timedelta
import re


class DateValidator(cli.switches.Validator):
    """
    A switch-type validator that checks the argument is a date
    """

    def __call__(self, obj):
        try:
            obj = date.fromisoformat(obj)
        except ValueError:
            print(obj + " is not a date in the correct format : %Y-%m-%d")
            exit(1)

        return obj

    def __repr__(self):
        return "Just a date validator"


class GithubLog(cli.Application):
    """
    Get commits since <date> of the current git directory, and create github links to see it.
    """
    verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")


    def main(self, date_since:DateValidator()=None):
        if date_since is None:
            date_since = date.today()

        date_since = date_since - timedelta(1)
        print("Used date : " + str(date_since))
        git = local["git"]
        commits = git(["log", "--oneline", f"--since={date_since}"])

        commits = commits.strip().split("\n")

        first_commit = commits[-1].split()[0]
        last_commit = commits[0].split()[0]
        previous_commit = git(["log", "--oneline", f"{first_commit}^", "-1"]).strip().split()[0]

        remote = re.search(r"dionisos2/(.*)\.git", git(["remote", "-v"])).group(1)

        result = f"https://github.com/dionisos2/{remote}/compare/{previous_commit}...{last_commit}"

        print(result)
        local["firefox-developer-edition"](result)



if __name__ == "__main__":
    GithubLog.run()


