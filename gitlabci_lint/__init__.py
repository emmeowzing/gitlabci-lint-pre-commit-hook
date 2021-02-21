import argparse
import json
import os

from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


parser = argparse.ArgumentParser()
parser.add_argument("base_url", nargs="?", default="https://gitlab.com/")
parser.add_argument("--token", default=os.getenv("GITLAB_TOKEN"))


def main(argv=None):
    args = parser.parse_args(argv)
    base_url = args.base_url
    token = args.token

    rv = 0
    try:
        with open(".gitlab-ci.yml", "r") as f:
            data = json.dumps({"content": f.read()})
    except (FileNotFoundError, PermissionError):
        print("Cannot open .gitlab-ci.yml")
        rv = 1
    else:
        url = urljoin(base_url, "/api/v4/ci/lint")
        msg_using_linter = "Using linter: " + url
        headers = {
            "Content-Type": "application/json",
            "Content-Length": len(data),
        }
        if token:
            headers["PRIVATE-TOKEN"] = token
            msg_using_linter += " with token " + len(token) * "*"
        print(msg_using_linter)
        try:
            request = Request(
                url,
                data.encode("utf-8"),
                headers=headers,
            )
            response = urlopen(request)
            lint_output = json.loads(response.read())

            if not lint_output["status"] == "valid":
                print("=======")
                for error in lint_output["errors"]:
                    print(error)
                rv = 1
                print("=======")
        except URLError as exc:
            print("Error connecting to Gitlab: " + str(exc))
            rv = 1
    return rv


if __name__ == "__main__":
    exit(main())
