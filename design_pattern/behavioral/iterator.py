def count_to(count):
    numbers = ["one", "two", "three", "four", "five"]
    yield from numbers[:count]

def count_to_two() -> None:
    return count_to(2)

def count_to_five() -> None:
    return count_to(5)

def main():
    """
    # Couting to two...
    >>> for number in count_to_two():
    ...     print(number)
    one
    two

    # Counting to five...
    >>> for number in count_to_five():
    ...     print(number)
    one
    two
    three
    four
    five
    """

if __name__ == "__main__":
    import doctest

    doctest.testmod()