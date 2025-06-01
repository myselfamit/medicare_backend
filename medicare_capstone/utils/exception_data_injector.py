import logging

def inject_data(exc, context, response):
    _module_name = context.get('view').__module__
    _exception_details = exc
    _response_details = response
    _response_data = response.data
    _context_details = context
    _view_details = context.get('view')
    _args = context.get('args')
    _kwargs = context.get('kwargs')
    _request_data = context.get('request').data
    _request_query_params = context.get('request').query_params

    logger = logging.getLogger(_module_name)

    logger.error(' || '.join([
        'EXCEPTION: {}'.format(_exception_details),
        'RESPONSE: {}'.format(_response_details),
        'RESPONSE DATA: {}'.format(_response_data),
        'CONTEXT: {}'.format(_context_details),
        'VIEW: {}'.format(_view_details),
        'ARGS: {}'.format(_args),
        'KWARGS: {}'.format(_kwargs),
        'DATA: {}'.format(_request_data),
        'QUERY PARAMS: {}'.format(_request_query_params)
    ]))