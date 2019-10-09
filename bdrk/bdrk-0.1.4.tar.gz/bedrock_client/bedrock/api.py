import os
from logging import Logger
from typing import Any, Dict, List, Tuple

import requests


class BedrockApi:
    def __init__(self, logger: Logger):
        self.logger = logger

        self.has_api_settings = False
        domain = os.environ.get("BEDROCK_API_DOMAIN")
        if not domain:
            self.logger.error("BEDROCK_API_DOMAIN not specified!")
            return

        # Using http to avoid cert issues for local development.
        # Will be redirected to https for staging.
        self.endpoint = f"{domain}/v1"

        self.token = os.environ.get("BEDROCK_API_TOKEN")
        if not self.token:
            self.logger.error("BEDROCK_API_TOKEN not specified!")
            return
        self.has_api_settings = True

    def post_json(self, url: str, post_data: Dict):
        if not self.has_api_settings:
            self.logger.error(f"No API settings to post json: {post_data}")
            return

        headers = {"content-type": "application/json", "X-Bedrock-Api-Token": self.token}
        try:
            response = requests.post(url, headers=headers, json=post_data, timeout=30)
            self.logger.info(
                f"Response: status_code={response.status_code}, data={response.json()}"
            )
        except Exception as ex:
            self.logger.exception(f"Error {ex} while posting json: {post_data}")

    def log_metric(self, key: str, value: Any):
        url = f"{self.endpoint}/run/metrics"
        post_data = {"key": key, "value": value}
        self.post_json(url=url, post_data=post_data)

    @staticmethod
    def _compute_tn_fp_fn_tp(actual: List[int], prediction: List[int]) -> Tuple:
        """Compute TN, FP, FN, TP.

        :param List[int] actual: Actual values
        :param List[int] prediction: Predicted values
        :return Tuple: TN, FP, FN, TP
        """
        tp = sum([p == 1 and a == 1 for p, a in zip(prediction, actual)])
        tn = sum([p == 0 and a == 0 for p, a in zip(prediction, actual)])
        fp = sum([p == 1 and a == 0 for p, a in zip(prediction, actual)])
        fn = len(actual) - tp - tn - fp
        return (tn, fp, fn, tp)

    def log_chart_data(self, actual: List[int], probability: List[float]):
        """Log prediction data for creating run metrics charts.

        :param List[int] actual: Actual values; must be 0 or 1.
        :param List[float] probability: Predicted probabilities produced by model;
                                        must be between 0 and 1.
        """

        if not all(map(lambda v: v in [0, 1], actual)):
            self.logger.error(f"log_chart_data: actual values must be 0 or 1: {actual}")
            return

        if not all(map(lambda v: 0.0 <= v and v <= 1.0, probability)):
            self.logger.error(
                f"log_chart_data: probability values must be between 0 and 1: {probability}"
            )
            return

        if not len(actual) == len(probability):
            self.logger.error(
                f"log_chart_data: mismatch in length of actual ({len(actual)}) "
                f"vs probability ({len(probability)}) values"
            )
            return

        chart_data = []
        thresholds = (x * 0.05 for x in range(0, 20))  # 0 to 1 in 0.05 increments
        for threshold in thresholds:
            prediction = [int(p > threshold) for p in probability]

            tn, fp, fn, tp = BedrockApi._compute_tn_fp_fn_tp(actual, prediction)

            chart_data.append({"threshold": threshold, "tn": tn, "fp": fp, "fn": fn, "tp": tp})

        self.log_metric("binary_classifier_chart", chart_data)
