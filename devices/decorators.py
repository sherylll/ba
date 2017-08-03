def aes_hmac_verified(function):
    def wrap(request, *args, **kwargs):
        

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap    