from ..utils.base_resource import BaseResource


class ApplicationsResource(BaseResource):
    resource_name = "applications"

    id_field = "application_id"

    searchable_fields = (
        "product",
        "status",
    )

    sortable_fields = (
        "application_id",
        "customer_id",
        "amount",
        "status",
    )
