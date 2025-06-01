from rest_framework.views import exception_handler
from medicare_capstone.utils.exception_data_injector import inject_data
def custom_exception_handler(exc, context):
    '''
        function is used to handle exceptions globally
    '''
    response = exception_handler(exc, context)

    if response is not None:
        if 'message' in response.data and response.data['message']:
            response.data = {
                'success': False,
                'status_code': response.status_code,
                'message': response.data['message'],
                'data': (
                    response.data['data'] if 'data' in response.data
                    else None
                )
            }
        else:
            response.data = {
                'success': False,
                'status_code': response.status_code,
                'message': response.data['detail'],
                'data': (
                    response.data['data'] if 'data' in response.data
                    else None
                )
            }

        # Adding Information for Exception
        inject_data(
            exc=exc,
            context=context,
            response=response
        )

    return response
