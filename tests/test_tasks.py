import asyncio
import threading

import pytest

from tasks import (
    add_user,
    create_users_table,
    fetch_json,
    get_user,
    make_failing_future,
    make_future,
    run_in_separate_thread,
    slow_square,
)


@pytest.mark.asyncio
async def test_1_future_resolves_with_expected_value(event_loop):
    future = make_future(42)

    assert isinstance(future, asyncio.Future)
    assert future.get_loop() is event_loop
    assert not future.done()

    result = await future

    assert result == 42
    assert future.done()


@pytest.mark.asyncio
async def test_2_future_is_rejected_with_expected_error(event_loop):
    future = make_failing_future(ValueError("Неверные данные"))

    with pytest.raises(ValueError, match="Неверные данные"):
        await future

    assert future.done()
    assert isinstance(future.exception(), ValueError)


@pytest.mark.asyncio
async def test_3_http_request_returns_correct_response(event_loop):
    status, data = await fetch_json("https://dog.ceo/api/breeds/image/random")

    assert status == 200
    assert data["status"] == "success"
    assert data["message"].startswith("https://images.dog.ceo/breeds/")


@pytest.mark.asyncio
async def test_4_database_function_adds_new_record(event_loop, tmp_path):
    db_path = tmp_path / "test.db"
    await create_users_table(db_path)

    user_id = await add_user(db_path, "Ivan", "ivan@example.com")
    saved_user = await get_user(db_path, user_id)

    assert user_id == 1
    assert saved_user == (1, "Ivan", "ivan@example.com")


@pytest.mark.asyncio
async def test_5_async_function_in_separate_thread_returns_result(event_loop):
    main_thread = threading.get_ident()
    worker_threads = []

    async def square_and_remember_thread(number):
        worker_threads.append(threading.get_ident())
        return await slow_square(number)

    result = await run_in_separate_thread(square_and_remember_thread, 7)

    assert result == 49
    assert worker_threads[0] != main_thread
