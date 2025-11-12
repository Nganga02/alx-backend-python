# UNIT TESTS

The `test_utils.TestAccessNestedMap` class is used to test if the path provided for the nessted map produces the desired result eg.
```python
nested_map={"a": 1}, path=("a",) expected_results = 1
nested_map={"a": {"b": 2}}, path=("a",) expected_results = {"b": 2}
nested_map={"a": {"b": 2}}, path=("a", "b") expected_results = 2
```

Using the `assertIsEqual` method to test the function `access_nested_map(nested_map: Mapping, path: Sequence)`
