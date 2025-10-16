def test_import_asgi_module():
    module = __import__("core.asgi", fromlist=["application"])
    assert hasattr(module, "application")


def test_import_wsgi_module():
    module = __import__("core.wsgi", fromlist=["application"])
    assert hasattr(module, "application")
