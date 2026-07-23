def paginate(data, page=1, page_size=25):
    total = len(data)

    total_pages = max(1, (total + page_size - 1) // page_size)

    start = (page - 1) * page_size

    end = start + page_size

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "data": data[start:end],
    }
