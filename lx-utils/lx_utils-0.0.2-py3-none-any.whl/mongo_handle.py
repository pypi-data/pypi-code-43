from mg_app_framework import TaskKey, get_handler, get_logger, get_organization, get_store


async def create_collection_and_index(collection_name: str, indexs: list) -> None:
    '''

    :param collection_name:
    :param indexs: [("item_code", 1), ("order_code", 1)]
    :return:
    '''
    handle = get_handler(TaskKey.mongodb_async)
    app_name = get_store().get_data()['app_module_name']
    db_name = get_organization() + '_' + app_name
    db = handle[db_name]
    collection_names = await db.list_collection_names(False)
    if collection_name not in collection_names:
        collection_current = await db.create_collection(collection_name)
        for index in indexs:
            await collection_current.create_index([index])
            get_logger().info('create collection[%s] and index %s success', collection_name, index)


def get_collection_handle(database_name='', collection_name=''):
    handle = get_handler(TaskKey.mongodb_async)
    app_name = get_store().get_data()['app_module_name']
    db_name = database_name if database_name else get_organization() + '_' + app_name
    return handle[db_name].get_collection(collection_name)
