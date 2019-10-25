import json
import os
import datetime

import numpy as np
# import the necessary packages
import pandas as pd

from forecastlib.evaluation.evaluation import CatalogProduct, EvaluatedProduct, EvaluatedCatalog
from forecastlib.models.ClassificationMLModel import ClassificationMLModel
from forecastlib.models.ForecastClassificator import ForecastClassificator
from forecastlib.models.ForecastClassificatorSingle import ForecastClassificatorSingle
from forecastlib.models.ForecastFlow import ForecastFlow
from forecastlib.models.ForecastModel import ForecastModel

from forecastlib.training.Metrics import Metrics
from .MappingService import MappingService

from applicationinsights import TelemetryClient

import logging

logger = logging.getLogger('ForecastService')

class ForecastService(object):
    def __init__(
            self,
            model_loader,
            models,
            classification_model_name: str = "forecast_classification_forest",
            classification_model_version: int = None,
            map_model_name: str = "forecast_map",
            map_model_version: int = None,
            product_data_model_name: str = "product_data",
            product_data_model_version: int = None,
            telemetry_client: TelemetryClient=None
    ):
        loaded_models = {}
        for name, model in models.items():
            m = model_loader.download(model.model_name, model.version)
            loaded_models[name] = ForecastModel.load(m)

        #classification_path = model_loader.download(classification_model_name, classification_model_version)
        #classification_model = ClassificationMLModel.load(classification_path)
        #classificator = ForecastClassificator(classification_model)
        classificator = ForecastClassificatorSingle()

        map_path = model_loader.download(map_model_name, map_model_version)
        map = self.load_map(map_path)
        product_data_path = model_loader.download(product_data_model_name, product_data_model_version)
        history = self.load_history(product_data_path)
        intents = self.load_intents(product_data_path)

        self.map_service = MappingService(map, history, intents)
        self.tc = telemetry_client
        self.wrapper = ForecastFlow(classificator=classificator, model_map=loaded_models)

    def log(self, message: str, ts):
        self.tc.track_metric(message, (datetime.datetime.now() - ts).total_seconds())

    def predict(self, original_data: np.array):
        df = self.map_service.from_json(original_data)
        ts = datetime.datetime.now()
        # mapped = self.map_service.apply_mapping(df)
        mapped = self.map_service.apply(df, self.get_cols())
        self.log("Mapping applied", ts)
        ts = datetime.datetime.now()

        # Predict input
        predictions, classifications = self.wrapper.predict(mapped)
        self.log("Prediction completed", ts)

        mapped["PREDICTED"] = predictions
        mapped["CLASSIFICATION"] = classifications

        return mapped

    def load_map(self, path: str):
        with open(path + os.path.sep + "map.json") as json_file:
            return json.load(json_file)

    def load_history(self, path: str):
        history = pd.read_csv(path + os.path.sep + "history.csv", sep=",")
        history["OFFER_PERC_M"] = history["OFFER_PERC_M"].astype(object)
        return history

    def load_intents(self, path: str):
        intents = pd.read_csv(path + os.path.sep + "intents.csv", sep=",")
        return intents

    def evaluate(self, forecasted_data: pd.DataFrame):
        #forecasted_data["NPU_RATIO"] = 1.573

        #forecasted_data["COST"] = np.where(forecasted_data["OFFER_PERC"] > 0, forecasted_data["OFFER_PRICE"] * 100.0 * 0.2 / forecasted_data["OFFER_PERC"], forecasted_data["OFFER_PRICE"])

        #forecasted_data["CONS_COST"] = np.where(forecasted_data["OFFER_PERC"] > 0, forecasted_data["OFFER_PRICE"] * 100.0 * 0.1 / forecasted_data["OFFER_PERC"], forecasted_data["OFFER_PRICE"])

        forecasted_data["UNITS_FORECAST"] = forecasted_data["ACTIVE_CONSULTANTS"].astype(float) * forecasted_data[
            "PREDICTED"]


        forecasted_data["GROSS_PRICE"] = forecasted_data["OFFER_PRICE"]
        forecasted_data["NET_PRICE"] = forecasted_data["GROSS_PRICE"] / forecasted_data["NPU_RATIO"]
        forecasted_data["NET_SALES"] = forecasted_data["NET_PRICE"] * forecasted_data["UNITS_FORECAST"]
        forecasted_data["COST_OF_SALES"] = forecasted_data["COST"] * forecasted_data["UNITS_FORECAST"]
        forecasted_data["CONS_COST_OF_SALES"] = forecasted_data["CONS_COST"] * forecasted_data["UNITS_FORECAST"]

        grouped = {}
        for y, x in forecasted_data.groupby("CAMPAIGN_CD"):
            c = {}
            c["active_count"] = x["ACTIVE_CONSULTANTS"].mean()
            c["products_count"] = x["PROD_ID"].shape[0]
            c["net_sales"] = x["NET_SALES"].sum()
            c["cost_of_sales"] = x["COST_OF_SALES"].sum()
            c["cons_cost_of_sales"] = x["CONS_COST_OF_SALES"].sum()
            c["units_total"] = x["UNITS_FORECAST"].sum()

            c["profit"] = c["net_sales"] - c["cost_of_sales"]
            c["cons_profit"] = c["net_sales"] - c["cons_cost_of_sales"]
            c["gross_margin"] = 1 - (c["cost_of_sales"] / c["net_sales"])
            c["cons_gross_margin"] = 1 - (c["cons_cost_of_sales"] / c["net_sales"])

            c["upa"] = x["UNITS_FORECAST"].sum() / c["active_count"]
            c["npu"] = c["net_sales"] / x["UNITS_FORECAST"].sum()
            c["spa"] = c["net_sales"] / c["active_count"]

            c["net_sales_by_group"] = {}
            c["units_by_group"] = {}

            for category, view in x.groupby("CATEGORY_CD"):
                c["net_sales_by_group"][category] = view["NET_SALES"].sum()
                c["units_by_group"][category] = view["UNITS_FORECAST"].sum()
            grouped[y] = c

        logger.info("Evaluation completed")
        return grouped

    def validate(self, forecasted_data: pd.DataFrame):
        validation = {}
        validation["total_accuracy"] = Metrics.model_accuracy(forecasted_data["UPA_ACTUAL"],
                                                              forecasted_data["PREDICTED"])

        for k, v in forecasted_data.groupby("CLASSIFICATION"):
            validation[k] = {}
            group = forecasted_data[forecasted_data["CLASSIFICATION"] == k]
            validation[k]["accuracy"] = Metrics.model_accuracy(group["UPA_ACTUAL"], group["PREDICTED"])
            validation[k]["count"] = group.shape[0]

        logger.info("Validation completed")
        return validation

    def get_cols(self):
        cols = list(self.map_service.cols.keys())
        for k, v in self.wrapper.model_map.items():
            cols += v.features

        logger.info("Validation completed")
        return list(set(cols))

