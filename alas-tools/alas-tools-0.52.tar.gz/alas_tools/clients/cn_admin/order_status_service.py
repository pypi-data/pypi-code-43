from alas_tools.clients.cn_admin.service_api_client import ServiceApiClient


class OrderStatusApiServiceClient(ServiceApiClient):
    service_endpoint_base_url = '/api/services/app/OrderStatus/'