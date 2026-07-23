from ..utils.base_resource import BaseResource


class AlertsResource(BaseResource):
    resource_name = "alerts"

    id_field = "alert_id"

    searchable_fields = (
        "category",
        "status",
    )

    sortable_fields = (
        "alert_id",
        "customer_id",
        "severity",
        "status",
    )
