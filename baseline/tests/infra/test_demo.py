def test_nginx_configuration(host):
    check = host.run("nginx -t")
    assert check.rc == 0, check.stderr


def test_release_content(host):
    index = host.file("/usr/share/nginx/html/index.html")
    assert index.is_file
    assert "devops6-demo" in index.content_string
