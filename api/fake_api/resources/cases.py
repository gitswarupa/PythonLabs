from ..utils.base_resource import BaseResource


class CasesResource(BaseResource):
    resource_name = "cases"

    id_field = "case_id"

    searchable_fields = (
        "owner",
        "status",
    )

    sortable_fields = (
        "case_id",
        "customer_id",
        "priority",
        "status",
    )
