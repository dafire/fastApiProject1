import time

from loguru import logger

if False:

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())
        # print("Start Query:\n" + str(statement) % parameters + "\n")

    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - conn.info["query_start_time"].pop(-1)
        logger.opt(depth=6).debug("{} [{:.5f}]", statement, total)

    event.listen(async_engine.sync_engine, "before_cursor_execute", before_cursor_execute)
    event.listen(async_engine.sync_engine, "after_cursor_execute", after_cursor_execute)
