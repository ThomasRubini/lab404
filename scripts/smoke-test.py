#!/usr/bin/env python3
"""Exercise the deployed polling application through its public HTTP interface."""

import argparse
import html
import json
import uuid
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


# Submit a form or fetch a page, following the application's redirects.
def request(url, form=None):
    data = urlencode(form, doseq=True).encode() if form is not None else None
    with urlopen(Request(url, data=data), timeout=10) as response:
        return response.geturl(), response.read().decode()


# Check the user-visible poll and vote totals at each step.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="Application URL, for example http://172.28.255.201")
    base = parser.parse_args().base_url.rstrip("/") + "/"
    question = f"Smoke test {uuid.uuid4().hex}"

    _, health = request(urljoin(base, "healthz"))
    if json.loads(health).get("status") != "ok":
        raise RuntimeError("Health check returned an unexpected response")

    poll_url, page = request(
        urljoin(base, "polls"),
        {"question": question, "choices": ["First", "Second"]},
    )
    if "/polls/" not in poll_url or html.escape(question) not in page:
        raise RuntimeError("Poll creation did not display the new poll")
    if "Results · 0 votes" not in page:
        raise RuntimeError("New poll did not start with zero votes")

    _, page = request(poll_url + "/votes", {"choice": "0"})
    if "Results · 1 vote" not in page or "First — 1" not in page:
        raise RuntimeError("First vote was not reflected in the results")

    _, page = request(poll_url + "/votes", {"choice": "1"})
    if "Results · 2 votes" not in page or "First — 1" not in page or "Second — 1" not in page:
        raise RuntimeError("Second vote was not reflected in the results")

    _, dashboard = request(urljoin(base, "polls"))
    entry = dashboard.split(html.escape(question), 1)
    if len(entry) != 2 or "2 votes · 2 choices" not in entry[1].split("</article>", 1)[0]:
        raise RuntimeError("Poll dashboard did not display the expected results")
    print(f"Smoke test passed: {poll_url}")


if __name__ == "__main__":
    main()
