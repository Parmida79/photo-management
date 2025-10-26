from functools import wraps

from fastapi import HTTPException


def path_id_validator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        path_parameters = kwargs['request'].path_params
        query_parameters = dict(kwargs['request'].query_params)
        path_parameters.update(query_parameters)

        if path_parameters is not None:
            for i in path_parameters:
                if i.endswith('id'):
                    try:
                        path_id = int(path_parameters[i])
                        if path_id <= 0:
                            # TODO: add i to message
                            raise HTTPException(status_code=404, detail='Id Not Found')

                    except (ValueError, TypeError):
                        i = i.replace('_', ' ').strip().title()
                        raise HTTPException(status_code=404, detail='Invalid ' + i + ' Given In Path')

        if query_parameters is not None:
            for i in query_parameters:
                if i is not None and (i.endswith('Id') or i.endswith('_id')):
                    try:
                        path_id = int(path_parameters[i])
                        if path_id <= 0:
                            # TODO: add i to message
                            raise HTTPException(status_code=404, detail='Id Not Found')

                    except (ValueError, TypeError):
                        i = i.replace('_', ' ').strip().title()
                        raise HTTPException(status_code=404, detail='Invalid ' + i + ' Given In Path')

        return func(*args, **kwargs)

    return wrapper


def convert_to_camel(word):
    i_s = word.split('_')
    output = ''

    if len(i_s) > 1:
        for i in range(len(i_s)):
            if i == 0:
                output = ''.join(i_s[0])
            else:
                i_s[i] = i_s[i].title()
                output = ''.join(i_s)
                i += 1
    else:
        output = ''.join(word)

    return output

