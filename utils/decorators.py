from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(method='GET', params=None):
    """
    @required_params(params=['some_param']) will return decorator func, and its
    parameter is the wrapped func, view_func

    For GET method, the params should be retrived in request.query_params,
    set it as the default
    For POST method, the params should be retrived in request.data
    """

    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator use wraps to pass the parameters of the view_func to
        _wrapped_view
        the instance is the self in view_func
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            missing_params = [
                param
                for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)

            # After completing the check the required params, call the
            # view_func wrapped by @required_params
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
