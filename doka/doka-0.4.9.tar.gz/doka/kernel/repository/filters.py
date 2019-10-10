def entity_filter(filter):
    def filter_function(entity):
        def calculate_operation(a, operation, b):
            if operation == '$eq':
                return a == b
            elif operation == '$neq':
                return a != b

        for field, condition in filter.items():
            if not isinstance(condition, dict):
                condition = {"$eq": condition}

            fl = True
            for operation, value in condition.items():
                if not calculate_operation(getattr(entity, field), operation, value):
                    fl = False
                    break
            if not fl:
                return False

        return True

    return filter_function
