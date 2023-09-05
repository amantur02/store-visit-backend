from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder

import usecases.customer_usecases
from exceptions import NotFoundException, DataValidationException, AccessDeniedException
from schemas.enums import OrderStatusEnum, UserRoleEnum
from schemas.order_schemas import OrderIn, Order, Store, VisitIn, Visit
from schemas.user_schemas import User
from usecases.customer_usecases import create_visit_usecase


@pytest.mark.asyncio
async def test_create_order_endpoint_success(sqlite_client, mocker):
    date = datetime.now()

    order_in = {
        "expires_at": date.isoformat(),
        "store_id": 1,
        "worker_id": 1
    }
    order = Order(
        id=1,
        created_at=date.isoformat(),
        expires_at=date.isoformat(),
        store_id=1,
        worker_id=1,
        customer_id=1,
        status=OrderStatusEnum.started
    )

    mocker.patch(
        "api.customer.customer_endpoints.create_order_usecase",
        return_value=order,
    )

    response = await sqlite_client.post(
        "/customers/create-order/", json=order_in
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "created_at": order.created_at.isoformat(),
        "expires_at": order.expires_at.isoformat(),
        "store_id": 1,
        "customer_id": 1,
        "status": OrderStatusEnum.started,
        "worker_id": 1,
    }


@pytest.mark.asyncio
async def test_create_order_fail_not_found(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.create_order_usecase",
        side_effect=NotFoundException,
    )
    response = await sqlite_client.post(
        "/customers/create-order/", json={
            "expires_at": datetime.now().isoformat(),
            "store_id": 1,
            "worker_id": 1
        }
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_order_fail_data_valid(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.create_order_usecase",
        side_effect=DataValidationException("Data validation order"),
    )
    response = await sqlite_client.post(
        "/customers/create-order/", json={
            "expires_at": datetime.now().isoformat(),
            "store_id": 1,
            "worker_id": 1
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        "message": "Data validation order",
        "error_code": "IncorrectDataError",
    }


@pytest.mark.asyncio
async def test_get_orders_success(sqlite_client, mocker):
    date = datetime.now()
    order = Order(
        id=1,
        created_at=date.isoformat(),
        expires_at=date.isoformat(),
        store_id=1,
        worker_id=1,
        customer_id=1,
        status=OrderStatusEnum.started
    )

    mocker.patch(
        "api.customer.customer_endpoints.get_orders_usecase",
        return_value=[order]
    )

    response = await sqlite_client.get(
        "/customers/orders/"
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "created_at": date.isoformat(),
            "expires_at": date.isoformat(),
            "store_id": 1,
            "customer_id": 1,
            "status": OrderStatusEnum.started,
            "worker_id": 1,
        },
    ]


@pytest.mark.asyncio
async def test_update_orders_success(sqlite_client, mocker):
    date = datetime.now()
    mocker.patch(
        "api.customer.customer_endpoints.update_order_usecase",
        return_value={
            "id": 1,
            "created_at": date.isoformat(),
            "expires_at": date.isoformat(),
            "store_id": 1,
            "worker_id": 1,
            "customer_id": 1,
            "status": OrderStatusEnum.started
        }
    )
    response = await sqlite_client.patch(
        "/customers/orders/1/",
        json={
            "id": 1,
            "created_at": date.isoformat(),
            "expires_at": date.isoformat(),
            "store_id": 1,
            "customer_id": 1,
            "status": OrderStatusEnum.started,
            "worker_id": 1,
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_orders_fail_not_found(sqlite_client, mocker):
    date = datetime.now()
    mocker.patch(
        "api.customer.customer_endpoints.update_order_usecase",
        side_effect=NotFoundException(),
    )
    response = await sqlite_client.patch(
        "/customers/orders/1/",
        json={
            "id": 1,
            "created_at": date.isoformat(),
            "expires_at": date.isoformat(),
            "store_id": 1,
            "customer_id": 1,
            "status": OrderStatusEnum.started,
            "worker_id": 1,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_order_success(sqlite_client, mocker):
    mocker.patch("api.customer.customer_endpoints.delete_order_usecase")
    response = await sqlite_client.delete("/customers/order/1/")
    assert response.status_code == 200
    assert response.json()["message"] == "Order with id: 1 deleted"


@pytest.mark.asyncio
async def test_delete_employee_fail(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.delete_order_usecase",
        side_effect=NotFoundException(),
    )
    response = await sqlite_client.delete("/customers/customers/order/1/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stores_success(sqlite_client, mocker):
    store = Store(
        id=1,
        title="store title",
    )

    mocker.patch(
        "api.customer.customer_endpoints.get_stores_usecase",
        return_value=[store],
    )

    response = await sqlite_client.get(
        "/customers/stores/", params={'id': 1}
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "store title"
        }
    ]


@pytest.mark.asyncio
async def test_create_visit_success(sqlite_client, mocker):
    date = datetime.now()

    visit_in = VisitIn(
        order_id=1
    )
    visit = Visit(
        id=1,
        created_at=date,
        worker_id=1,
        order_id=1,
        customer_id=1,
        store_id=1
    )

    mocker.patch(
        "api.customer.customer_endpoints.create_visit_usecase",
        return_value=visit,
    )

    response = await sqlite_client.post(
        "/customers/create-visit/", json=visit_in.model_dump()
    )
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "created_at": date.isoformat(),
        "worker_id": 1,
        "order_id": 1,
        "customer_id": 1,
        "store_id": 1,
    }


@pytest.mark.asyncio
async def test_create_visit_fail_access_denied(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.create_visit_usecase",
        side_effect=AccessDeniedException("Access denied"),
    )
    response = await sqlite_client.post(
        "/customers/create-visit/", json={
            "id": 1,
            "created_at": datetime.now().isoformat(),
            "worker_id": 1,
            "order_id": 1,
            "customer_id": 1,
            "store_id": 1
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_visit_fail_data_valid(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.create_visit_usecase",
        side_effect=DataValidationException(),
    )
    response = await sqlite_client.post(
        "/customers/create-visit/",
        json={
            "order_id": 1
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_visits_success(sqlite_client, mocker):
    date = datetime.now()

    visit = Visit(
        id=1,
        created_at=date,
        worker_id=1,
        order_id=1,
        customer_id=1,
        store_id=1
    )

    mocker.patch(
        "api.customer.customer_endpoints.get_visits_usecase",
        return_value=[visit],
    )

    response = await sqlite_client.get(
        "/customers/visits/", params={'order_id': 1}
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "created_at": date.isoformat(),
            "worker_id": 1,
            "order_id": 1,
            "customer_id": 1,
            "store_id": 1,
        }
    ]


@pytest.mark.asyncio
async def test_delete_order_success(sqlite_client, mocker):
    mocker.patch("api.customer.customer_endpoints.delete_visit_usecase")
    response = await sqlite_client.delete("/customers/visit/1/")
    assert response.status_code == 200
    assert response.json()["message"] == "Visit with id 1 deleted"


@pytest.mark.asyncio
async def test_delete_order_fail(sqlite_client, mocker):
    mocker.patch(
        "api.customer.customer_endpoints.delete_visit_usecase",
        side_effect=NotFoundException(),
    )
    response = await sqlite_client.delete("/customers/visit/1/")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_order_status_success(sqlite_client, mocker):
    order = Order(
        id=1,
        status=OrderStatusEnum.started
    )

    mocker.patch(
        "api.customer.customer_endpoints.update_order_status_usecase",
        return_value=order.model_dump(),
    )

    response = await sqlite_client.put(f"/customers/order/{order.id}/status/", json={"status": order.status})

    assert response.status_code == 200

    assert "id" in response.json()
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_update_order_status_fail_not_found(sqlite_client, mocker):
    order_id = 999

    mocker.patch(
        "api.customer.customer_endpoints.update_order_status_usecase",
        side_effect=NotFoundException("Not found order"),
    )

    response = await sqlite_client.put(f"/customers/order/{order_id}/status/", json={"status": "ended"})

    assert response.status_code == 404

    assert "message" in response.json()
    assert "error_code" in response.json()
