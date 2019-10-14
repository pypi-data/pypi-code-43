import requests


def sesame_lists(token: str, endpoint: str) -> list:
    sesame_api_url = f"https://sesame.brainlabsdigital.com/api/{endpoint}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(sesame_api_url, headers=headers)

    try:
        assert response.status_code == 200
        return sorted([i["name"] for i in response.json()])
    except Exception:
        raise requests.RequestException


def tags(token: str) -> list:
    try:
        return sesame_lists(token, "tag")
    except requests.RequestException:
        return [
            "247-bidding",
            "ab-labs",
            "ad-params",
            "analysing",
            "auction-insights",
            "audiences",
            "bidding",
            "big-red-stop-button",
            "brsb",
            "budget-tracker",
            "budgets",
            "building",
            "ckp-tech",
            "gantt",
            "keyword-bidding",
            "managing",
            "monitoring",
            "pausing/unpausing",
            "protecting",
            "reporting",
            "sesame",
            "shopping",
            "spend",
            "syncing",
            "tech-adoption",
            "tech-tracking",
            "testing",
            "tv",
        ]


def platforms(token: str) -> list:
    try:
        return sesame_lists(token, "platform")
    except requests.RequestException:
        return [
            "amazon-advertising",
            "amazon-s3",
            "apple-search-ads",
            "aws-lambda",
            "aws-sns",
            "bing-ads",
            "bob",
            "clockify",
            "dv360",
            "facebook-ads",
            "file-processing",
            "github",
            "google-admin",
            "google-ads",
            "google-analytics",
            "google-bigquery",
            "google-calendar",
            "google-campaign-manager",
            "google-content",
            "google-docs",
            "google-drive",
            "google-forms",
            "google-mail",
            "google-sheets",
            "google-slides",
            "hubspot",
            "ltd-api",
            "pepper",
            "search-ads-360",
            "sesame",
            "similarweb",
            "slack",
            "snapchat-ads",
            "timetastic",
            "trello",
            "twitter-ads",
            "web-scraping",
        ]


def deployments(token: str) -> list:
    try:
        return sesame_lists(token, "deployment")
    except requests.RequestException:
        return [
            "server-cronjob",
            "tech-managed-google-ads-script",
            "user-managed-google-ads-script",
            "server-button-press",
            "web-app",
            "tech-managed-apps-script",
            "user-managed-apps-script",
            "command-line",
            "glitch",
            "aws-lambda-function",
            "pepper",
        ]


def departments(token: str) -> list:
    try:
        return sesame_lists(token, "department")
    except requests.RequestException:
        return [
            "All",
            "Analytics & CRO",
            "Biddable",
            "Biddable/Programmatic",
            "Biddable/Search",
            "Biddable/Social",
            "Finance",
            "New Business & Marketing",
            "Office Management",
            "Onboarding & Strategy",
            "Operations",
            "People Operations",
            "Tech",
        ]


def servers(token: str) -> list:
    try:
        return sesame_lists(token, "server")
    except requests.RequestException:
        return [
            "amazon-lambda",
            "binghorse",
            "brand-protect",
            "campaign-builder",
            "old-project-y",
            "project-y",
            "shiny-playground",
            "shopping",
            "shopping-builder",
            "sqrt",
            "workhorse1",
            "workhorse2",
            "workhorse3",
            "workhorse4",
        ]
