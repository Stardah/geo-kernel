from geokernel.client import Client


def test():
    client = Client("9090", "45.141.22.192")
    # client.login_request()
    client.request_ws("webgis algebra -id 15 -v \"huihui\"")

test()