def add_cache_header(app, max_age):
    def func(response):
        if max_age > 0 and response.status_code == 200:
            response.cache_control.max_age = max_age
        if max_age == 0:
            response.cache_control.no_cache = True
        return response
    app.after_request(func)
