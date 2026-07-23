from fake_api import FakeAPI


def print_response(title, response):
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(f"Status Code: {response.status_code}")
    print(response.json())
    print()


def main():
    api = FakeAPI(api_key="training-key")

    # -----------------------------------------------------------------
    # GET ALL
    # -----------------------------------------------------------------

    response = api.customers.list()

    print_response("GET ALL CUSTOMERS", response)

    # -----------------------------------------------------------------
    # GET ONE
    # -----------------------------------------------------------------

    response = api.customers.get(1)

    print_response("GET CUSTOMER 1", response)

    # -----------------------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------------------

    response = api.customers.list(
        page=2,
        page_size=10,
    )

    print_response("PAGINATION", response)

    # -----------------------------------------------------------------
    # FILTERING
    # -----------------------------------------------------------------

    response = api.customers.list(
        country="US",
        risk_level="HIGH",
    )

    print_response("FILTERING", response)

    # -----------------------------------------------------------------
    # SORTING
    # -----------------------------------------------------------------

    response = api.customers.list(
        sort="credit_score",
        order="desc",
    )

    print_response("SORTING", response)

    # -----------------------------------------------------------------
    # SEARCH
    # -----------------------------------------------------------------

    response = api.customers.list(
        search="john",
    )

    print_response("SEARCH", response)

    # -----------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------

    response = api.customers.create(
        {
            "first_name": "Andres",
            "last_name": "Miranda",
            "email": "andres@example.com",
            "country": "Costa Rica",
            "credit_score": 780,
            "risk_level": "LOW",
            "status": "ACTIVE",
        }
    )

    print_response("CREATE", response)

    new_customer = response.data["customer_id"]

    # -----------------------------------------------------------------
    # PATCH
    # -----------------------------------------------------------------

    response = api.customers.patch(
        new_customer,
        {
            "credit_score": 810,
            "risk_level": "LOW",
        },
    )

    print_response("PATCH", response)

    # -----------------------------------------------------------------
    # PUT
    # -----------------------------------------------------------------

    response = api.customers.update(
        new_customer,
        {
            "first_name": "Andres",
            "last_name": "Miranda-Arias",
            "email": "andres@example.com",
            "country": "Costa Rica",
            "credit_score": 825,
            "risk_level": "LOW",
            "status": "ACTIVE",
        },
    )

    print_response("PUT", response)

    # -----------------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------------

    response = api.customers.delete(new_customer)

    print_response("DELETE", response)


if __name__ == "__main__":
    main()
