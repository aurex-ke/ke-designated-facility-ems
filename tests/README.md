# Tests

The tests use only the Python standard library (`unittest`), so nothing needs
installing. Run them from the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -t . -v
```

`PYTHONPATH=src` lets Python find the `ke_ems` package without installing it.
`pytest` can also collect these tests if it is ever added; it is not required.
