

def get_param(request, param):
    if param in request.GET:
        return request.GET[param]
    else:
        return ''