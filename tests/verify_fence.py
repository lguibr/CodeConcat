# -*- coding: utf-8 -*-
from codeconcat.output import get_safe_fence


def test_safe_fence():
    # Case 1: No backticks
    content1 = "print('hello')"
    assert get_safe_fence(content1) == "```", f"Failed Case 1: {get_safe_fence(content1)}"

    # Case 2: 3 backticks inside
    content2 = "```python\ncode\n```"
    assert get_safe_fence(content2) == "````", f"Failed Case 2: {get_safe_fence(content2)}"

    # Case 3: 4 backticks inside
    content3 = "````text\ninner fence\n````"
    assert get_safe_fence(content3) == "`````", f"Failed Case 3: {get_safe_fence(content3)}"

    # Case 4: Multiple backtick groups
    content4 = "`inline` and ```block```"
    assert get_safe_fence(content4) == "````", f"Failed Case 4: {get_safe_fence(content4)}"

    print("All fence tests passed!")


if __name__ == "__main__":
    test_safe_fence()
