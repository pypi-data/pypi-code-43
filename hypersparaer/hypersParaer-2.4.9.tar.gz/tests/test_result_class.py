import pandas as pd
from paraer.vendor import HTTPResult, HTTPPaginator
from rest_framework.test import APIClient, APITestCase, APIRequestFactory


class ResultClassTestCase(APITestCase):
    def test_dict(self):
        data = {"a": "b"}
        request = APIRequestFactory().get("/api")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(data)
        self.assertEqual(response.data, data)

    def test_list(self):
        data = [{"a": "b"}]
        request = APIRequestFactory().get("/api")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(data)
        self.assertEqual(response.data["records"], data)

    def test_csv(self):
        data = [{"a": "b"}]
        request = APIRequestFactory().get("/api", content_type="text/csv")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(
            data, filename="test.csv"
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

        df = pd.DataFrame(data)
        response = HTTPResult(request=request, paginator=paginator).response(
            df, filename="test.csv"
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

    def test_csv_extractor(self):
        data = dict(data=[{"a": "b"}])
        request = APIRequestFactory().get("/api", content_type="text/csv")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(
            data, filename="test.csv", extractor=lambda x: x["data"]
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

        df = pd.DataFrame(data["data"])
        response = HTTPResult(request=request, paginator=paginator).response(
            df, filename="test.csv", extractor=lambda x: x["data"]
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

    def test_csv_blank(self):
        data = dict(data=[])
        request = APIRequestFactory().get("/api", content_type="text/csv")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(
            data, filename="test.csv", extractor=lambda x: x["data"]
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

        df = pd.DataFrame(data["data"])
        response = HTTPResult(request=request, paginator=paginator).response(
            df, filename="test.csv", extractor=lambda x: x["data"], header=["a", "b"]
        )
        self.assertEqual(response.get("content-type"), "text/csv")
        self.assertEqual(
            response.get("Content-Disposition"), "attachment; filename=test.csv"
        )

    def test_paginate(self):
        data = [{'a': 'b'}]
        request = APIRequestFactory().get("/api")
        paginator = HTTPPaginator()
        paginator.request = request

        response = HTTPResult(request=request, paginator=paginator).response(
            data, paginate=False
        )
        self.assertEqual(response.data, data)

        response = HTTPResult(request=request, paginator=paginator).response(
            data, paginate=True
        )
        self.assertEqual(response.data['records'], data)