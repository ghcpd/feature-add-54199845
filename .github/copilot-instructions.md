# Workflow

The environment variable `DEPS_IMAGE` contains the Docker image with all dependencies pre-installed.
**All project code and tests MUST run inside this container:**

```bash
docker run --rm -v "$(pwd):/repo" -w /repo "$DEPS_IMAGE" python3 -m pytest tests/test_requests.py::TestRequests::test_header_no_return_chars[invalid_header11] tests/test_requests.py::TestRequests::test_header_no_return_chars[invalid_header8] tests/test_requests.py::TestRequests::test_header_no_return_chars[invalid_header9] -xvs
```

Do NOT `pip install` on the host — the container already has everything.
Make sure all tests passed after making changes.
