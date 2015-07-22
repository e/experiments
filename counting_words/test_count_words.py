# run this test by using py.test:
# (pip install pytest)
# $> py.test -k test_count_words


from count_words import count_words


def test_count_words():
    lines = [
        "Little pig, let me come in.",
        "No, no, no, no, not by the hair on my little chin chin.",
    ]
    expected_top_three = [('no', 4), ('chin', 2), ('little', 2)]
    assert count_words(lines)[:3] == expected_top_three
