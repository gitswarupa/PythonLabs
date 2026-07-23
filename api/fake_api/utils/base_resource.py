from __future__ import annotations

import random
from copy import deepcopy
from typing import Any, ClassVar

from fake_api.database import DATABASE
from fake_api.response import Response

from .auth import check_api_key
from .delay import simulate_delay
from .filters import apply_filters
from .pagination import paginate


class BaseResource:
    resource_name: ClassVar[str] = ""
    id_field: ClassVar[str] = ""

    searchable_fields: ClassVar[tuple[str, ...]] = ()
    sortable_fields: ClassVar[tuple[str, ...]] = ()

    def __init__(self, config) -> None:
        self.config = config
        self.data = DATABASE[self.resource_name]

    ###############################################################

    def _failure(self) -> Response | None:
        r = random.random()

        if r < self.config.timeout_rate:
            return Response(
                status_code=504,
                error="Gateway Timeout",
            )

        if r < self.config.failure_rate:
            return Response(
                status_code=500,
                error="Internal Server Error",
            )

        return None

    ###############################################################

    def list(
        self,
        page: int = 1,
        page_size: int | None = None,
        search: str | None = None,
        sort: str | None = None,
        order: str = "asc",
        **filters: Any,
    ) -> Response:
        auth = check_api_key(self.config)

        if auth:
            return auth

        failure = self._failure()

        if failure:
            return failure

        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        records = deepcopy(self.data)

        ###########################################################
        # Filters
        ###########################################################

        records = apply_filters(
            records,
            filters,
        )

        ###########################################################
        # Search
        ###########################################################

        if search:
            search = search.lower()

            results = []

            for record in records:
                for field in self.searchable_fields:
                    value = str(record.get(field, "")).lower()

                    if search in value:
                        results.append(record)
                        break

            records = results

        ###########################################################
        # Sorting
        ###########################################################

        if sort in self.sortable_fields:
            records.sort(
                key=lambda record: record.get(sort),
                reverse=order.lower() == "desc",
            )

        ###########################################################

        page_size = page_size or self.config.default_page_size

        payload = paginate(
            records,
            page,
            page_size,
        )

        return Response(
            status_code=200,
            data=payload,
            processing_time_ms=elapsed,
        )

    ###############################################################

    def get(self, item_id: int) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        for record in self.data:
            if record[self.id_field] == item_id:
                return Response(
                    status_code=200,
                    data=deepcopy(record),
                    processing_time_ms=elapsed,
                )

        return Response(
            status_code=404,
            error=f"{self.resource_name[:-1].title()} not found",
            processing_time_ms=elapsed,
        )

    ###############################################################

    def create(self, record: dict[str, Any]) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        next_id = max(item[self.id_field] for item in self.data) + 1

        record[self.id_field] = next_id

        self.data.append(record)

        return Response(
            status_code=201,
            data=deepcopy(record),
            processing_time_ms=elapsed,
        )

    ###############################################################

    def update(
        self,
        item_id: int,
        record: dict[str, Any],
    ) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        for index, current in enumerate(self.data):
            if current[self.id_field] == item_id:
                record[self.id_field] = item_id

                self.data[index] = record

                return Response(
                    status_code=200,
                    data=deepcopy(record),
                    processing_time_ms=elapsed,
                )

        return Response(
            status_code=404,
            error="Resource not found",
            processing_time_ms=elapsed,
        )

    ###############################################################

    def patch(
        self,
        item_id: int,
        values: dict[str, Any],
    ) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        for record in self.data:
            if record[self.id_field] == item_id:
                record.update(values)

                return Response(
                    status_code=200,
                    data=deepcopy(record),
                    processing_time_ms=elapsed,
                )

        return Response(
            status_code=404,
            error="Resource not found",
            processing_time_ms=elapsed,
        )

    ###############################################################

    def delete(self, item_id: int) -> Response:
        elapsed = simulate_delay(
            self.config.min_delay,
            self.config.max_delay,
        )

        for index, record in enumerate(self.data):
            if record[self.id_field] == item_id:
                deleted = self.data.pop(index)

                return Response(
                    status_code=200,
                    data=deepcopy(deleted),
                    processing_time_ms=elapsed,
                )

        return Response(
            status_code=404,
            error="Resource not found",
            processing_time_ms=elapsed,
        )
