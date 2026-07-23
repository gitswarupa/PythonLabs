from ..utils.base_resource import BaseResource


class CustomersResource(BaseResource):
    resource_name = "customers"

    id_field = "customer_id"

    searchable_fields = (
        "first_name",
        "last_name",
        "email",
    )

    sortable_fields = (
        "customer_id",
        "credit_score",
        "country",
        "risk_level",
        "status",
    )
