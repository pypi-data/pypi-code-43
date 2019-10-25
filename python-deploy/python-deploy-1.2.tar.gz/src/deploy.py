#!/usr/bin/python3

import argparse
from datetime import datetime
import json
import subprocess
from typing import List
import tempfile
import os
from enum import Enum


HISTORY_FILE = os.path.expanduser("~/.deploy_history")


def check_call(params: List[str]) -> bytes:
    with tempfile.TemporaryFile() as logfile:
        try:
            subprocess.check_call(params, stdout=logfile)
        except subprocess.SubprocessError:
            logfile.seek(0)
            logs = logfile.read()
            print("[!] Called process error:")
            print(logs.decode("utf-8"))
            raise
        logfile.seek(0)
        return logfile.read()


def is_clean_repo() -> bool:
    status = check_call(["git", "status", "--short"])
    return status.strip() == b""


def get_current_git_hash() -> str:
    return check_call(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")


def tag_docker_image(existing_image: str, new_tag: str) -> None:
    check_call(["sudo", "docker", "tag", existing_image, new_tag])


def build_image(image_cfg, tag, no_cache: bool):
    no_cache_param = ["--no-cache"] if no_cache else []
    check_call(
        [
            "sudo",
            "docker",
            "image",
            "build",
            image_cfg.get("dir", "src"),
            "-t",
            tag,
            "-f",
            image_cfg.get("dockerfile", "deploy/docker/Dockerfile"),
        ]
        + no_cache_param
    )


def push_image(tag):
    check_call(["sudo", "docker", "image", "push", tag])


def redeploy(k8s_config, tag):
    check_call(
        [
            "kubectl",
            "set",
            "image",
            "--namespace",
            k8s_config["namespace"],
            "deployment/{}".format(k8s_config["deployment"]),
            "{}={}".format(k8s_config["container"], tag),
        ]
    )


def get_current_image(k8s_config):
    container = k8s_config["container"]
    jsonpath = f'{{..containers[?(@.name=="{container}")].image}}'
    return check_call(
        [
            "kubectl",
            "get",
            "deployment",
            "--namespace",
            k8s_config["namespace"],
            f"-o=jsonpath={jsonpath}",
        ]
    ).decode("utf-8")


def build_all(config, push: bool, deploy: bool, version, no_cache: bool):
    for name, element in config.items():
        tag = "{}:{}".format(element["docker"]["image"], version)
        if "docker" in element:
            print("[-] Building {}".format(name))
            build_image(element["docker"], tag, no_cache)
            print("[-] Built image {}".format(tag))
            if push:
                print("[-] Pushing image {}".format(tag))
                push_image(tag)
        if deploy is not None:
            key = "k8s" if deploy == "production" else "k8s-staging"
            if key not in element:
                print("[!] {} is missing a {} config".format(name, key))
                continue
            if deploy == "production":
                master = "{}:{}".format(element["docker"]["image"], "master")
                print("[-] Pushing image {}".format(master))
                tag_docker_image(tag, master)
            latest = "{}:{}".format(element["docker"]["image"], "latest")
            print("[-] Pushing image {}".format(latest))
            tag_docker_image(tag, latest)
            push_image(latest)
            previous_tag = get_current_image(element[key])
            print("[-] Old image was {}".format(previous_tag))
            if previous_tag == tag:
                print("[-] Image unchanged, not deploying")
            else:
                print("[-] Deploying {} to {}".format(tag, deploy))
                redeploy(element[key], tag)
                update_history_file(name, key, element, previous_tag, tag)


class ImageTagSource(Enum):
    commit_hash = "commit_hash"
    date = "date"
    latest = "latest"

    def __str__(self) -> str:
        return self.value


def read_history_file():
    if not os.path.isfile(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as histf:
        raw_data = histf.read()
    return [json.loads(elm) for elm in raw_data.split("\n") if elm.strip()]


def write_history_file(data):
    raw_data = "\n".join(json.dumps(elm) for elm in data)
    with open(HISTORY_FILE, "w") as histf:
        histf.write(raw_data)


def update_history_file(name, key, element, previous_image, new_image):
    data = read_history_file()
    data.append(
        {
            "timestamp": int(datetime.now().timestamp()),
            "service": name,
            "element": element,
            "key": key,
            "previous_image": previous_image,
            "new_image": new_image,
        }
    )
    write_history_file(data)


def get_k8s_namespaces():
    ns_bytes = check_call(["kubectl", "get", "namespaces"])
    ns_text = ns_bytes.decode("utf-8")
    namespaces = []
    for line in ns_text.split("\n")[1:]:
        if not line.strip():
            continue
        namespaces.append(line.split()[0])
    return namespaces


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy the application.")
    parser.add_argument(
        "service", default=None, nargs="?", help="Service to deploy"
    )
    parser.add_argument(
        "--history",
        "-H",
        action="store_true",
        help="Instead of doing anything, show a deploy history.",
    )
    parser.add_argument(
        "--no-cache",
        "-B",
        action="store_true",
        help="Pass --no-cache to docker build",
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force deploy. It's probably a bad idea.",
    )
    parser.add_argument(
        "--build", "-b", action="store_true", help="Only build images"
    )
    parser.add_argument(
        "--push", action="store_true", help="Build and push images"
    )
    parser.add_argument(
        "--production",
        "-p",
        action="store_true",
        help="Build, push and redeploy images TO PRODUCTION",
    )
    parser.add_argument(
        "--staging",
        "-s",
        action="store_true",
        help="Build, push and redeploy images to the staging environment",
    )
    parser.add_argument(
        "--promote",
        "-P",
        action="store_true",
        help="Promote image from staging to the production environment",
    )
    parser.add_argument(
        "--tag",
        "-t",
        type=ImageTagSource,
        default=ImageTagSource.commit_hash,
        choices=list(ImageTagSource),  # type: ignore
        help="How to name a docker image.",
    )
    args = parser.parse_args()

    if args.build:
        push, deploy = False, None
    elif args.push:
        push, deploy = True, None
    elif args.production:
        push, deploy = True, "production"
    elif args.staging:
        push, deploy = True, "staging"
    elif args.promote or args.history:
        pass
    else:
        print("What do you want to do? (try --production or --help)")
        return

    with open("deploy/deploy.json", "r") as configfile:
        config = json.loads(configfile.read())

    if args.service is not None:
        config = {args.service: config[args.service]}

    if args.history:
        history = read_history_file()
        logs = [elm for elm in history if elm["service"] in config.keys()]
        for log_entry in logs:
            timestamp = datetime.fromtimestamp(
                log_entry["timestamp"]
            ).isoformat()
            key = log_entry.get("key", "unknown")
            service = log_entry["service"]
            prev_img = log_entry["previous_image"]
            new_img = log_entry["new_image"]
            print(f"{timestamp} [{key}] {service}: {prev_img} -> {new_img}")
        return

    if not is_clean_repo():
        if args.force:
            if args.tag == ImageTagSource.commit_hash:
                print(
                    "Warning: repo is dirty. "
                    + "Tagging with git hash may give unexpected results."
                )
            if args.production:
                print("Is everything OK at home?. Ok, deploying...")
        else:
            print("You have uncommited changes. Commit them (or --force).")
            return
    if args.promote:
        for name, element in config.items():
            tag = get_current_image(element["k8s-staging"])
            print(f"[-] Redeploying {tag} to production")
            redeploy(element["k8s"], tag)
            base, _version = tag.split(":")
            new_tag = f"{base}:master"
            print("[-] Tagging {} as {}".format(tag, new_tag))
            tag_docker_image(tag, new_tag)
    else:
        if args.tag == ImageTagSource.commit_hash:
            version = get_current_git_hash()
        elif args.tag == ImageTagSource.date:
            version = datetime.utcnow().strftime("v%Y%m%d%H%M%S")
        elif args.tag == ImageTagSource.latest:
            version = "latest"
        else:
            raise RuntimeError("[!] Unsupported tag type")
        no_cache = args.no_cache
        build_all(config, push, deploy, version, no_cache)


if __name__ == "__main__":
    main()
