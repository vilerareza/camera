def app(environ, start_response):
    data = b'Hello'
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content_Length', str(len(data)))
        ]
    start_response(status, response_headers)
    return iter([data])