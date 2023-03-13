from main import AnimalsTable, Animal
from pytest import fixture

@fixture
def animals_table() -> AnimalsTable:
    return AnimalsTable()

def test_get_animals_set(animals_table):
    animals_set = animals_table.animals_set()
    animals_names = {animal.name for animal in animals_set}
    # test over a fixed set of animals with varying properties in the wiki page
    # Make sure test animals have a collateral adjective
    for test_animal in ["Eagle", "Elephant seal", "Goat", "Ram"]:
        assert test_animal in animals_names

def test_is_row_an_animal(animals_table):
    header_row = animals_table.get_wiki_table_row(0)
    letter_row = animals_table.get_wiki_table_row(1)
    alpaca_row = animals_table.get_wiki_table_row(5)
    bat_row = animals_table.get_wiki_table_row(16)
    expected_results = [
        (header_row, False),
        (letter_row, False),
        (alpaca_row, True),
        (bat_row, True)
    ]
    assert all(
        Animal.is_row_an_animal(row) == result for row, result in expected_results
    )