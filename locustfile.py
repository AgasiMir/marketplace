from locust import HttpUser, task, between


# Перед запуском нагрузочного тестирования, нужно отключить rate limiter у ручек
# locust -f locustfile.py --host=http://localhost:8000


class MarketplaceUser(HttpUser):
    wait_time = between(1, 3)

    @task(8)
    def get_products(self):
        self.client.get(
            "/products",
            params={
                "sort_by": "price",
                "sort_order": "desc",
                "page": 1,
                "page_size": 10,
            },
        )

    @task(8)
    def get_products_page_size_20(self):
        self.client.get(
            "/products",
            params={
                "sort_by": "created_at",
                "sort_order": "desc",
                "page": 1,
                "page_size": 20,
            },
        )

    @task(8)
    def get_products_page_2(self):
        self.client.get(
            "/products",
            params={
                "sort_by": "created_at",
                "sort_order": "desc",
                "page": 2,
                "page_size": 10,
            },
        )

    @task(4)
    def get_product(self):
        self.client.get(
            "/products/2",
        )

    @task(4)
    def get_product_2(self):
        self.client.get(
            "/products/3",
        )

    @task(4)
    def get_product_by_category(self):
        self.client.get(
            "/products/category/1",
        )

    @task(2)
    def get_categories(self):
        self.client.get(
            "/categories",
            params={
                "sort_by": "created_at",
                "sort_order": "asc",
                "page": 1,
                "page_size": 10,
            },
        )
