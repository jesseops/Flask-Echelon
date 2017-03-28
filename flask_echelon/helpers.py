# -*- coding: utf-8 -*-


def has_access(echelon):
    """
    Check if `current_user` has access to an Echelon in `current_app`

    :return: bool
    """
    if not hasattr(current_app, 'echelon_manager'):
        raise Exception("Flask app '{!r}' does not have a bound interaction manager".format(current_app))
    return current_app.echelon_manager.check_access(current_user, echelon)


def require_echelon(echelon):
    """
    Check if `current_user` has access to an Echelon in `current_app`
    If check fails, raise `AccessCheckFailed`
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_app.echelon_manager.check_access(current_user, echelon):
                return func(*args, **kwargs)
            raise AccessCheckFailed('{} does not have access to Echelon "{}"'.format(current_user, echelon))
        return wrapper
    return decorator
