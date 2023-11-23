def add_cache_header(app, max_age=600):
    def func(response):
        response.cache_control.max_age = max_age
        return response
    app.after_request(func)
