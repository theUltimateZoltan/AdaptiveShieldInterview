import enum
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Dict, Union, List
from collections import defaultdict
import requests
from copy import copy

class Column(enum.Enum):
    ANIMAL= 0
    COLLATERAL_ADJ= 5

class Animal:
    def __init__(self, row: Tag):
        if not Animal.is_row_an_animal(row):
            raise ValueError("Row does not represent an animal")

        details = Animal.extract_details_from_row(row)
        unprocessed_collaterals = details[Column.COLLATERAL_ADJ.value].get_text(strip=True,
                                                                                     separator='\n').splitlines()
        self.collateral_adjectives = Animal.process_collateral_adjectives(unprocessed_collaterals)
        unprocessed_name = details[Column.ANIMAL.value].text
        self.name = Animal.process_name(unprocessed_name)

    @staticmethod
    def extract_details_from_row(row: Tag) -> Union[list, None]:
        animal_details = row.select("td")
        if len(animal_details) > 1:  # rows representing animals have multiple details
            return animal_details

    @staticmethod
    def is_row_an_animal(row: Tag) -> bool:
        return bool(Animal.extract_details_from_row(row))

    @staticmethod
    def process_name(name: str) -> str:
        exit_phrases = ["(", "[", " also see", " see"]
        stripped_name = copy(name).capitalize()
        for exit_phrase in exit_phrases:
            stripped_name = stripped_name.split(exit_phrase)[0]
        return stripped_name.strip()

    @staticmethod
    def process_collateral_adjectives(adjectives: List[str]) -> List[str]:
        return [adj.capitalize().strip() for adj in adjectives if adj.isalpha()]  # screen redundant comments and marks

class AnimalsTable:
    def __init__(self):
        table_element = AnimalsTable.get_animals_table_element()
        self.__collateral_adjective_map = AnimalsTable.parse_html_table(table_element)

    @staticmethod
    def get_animals_table_element() -> Tag:
        page_html = requests.get("https://en.wikipedia.org/wiki/List_of_animal_names").content
        page = BeautifulSoup(page_html, features="html.parser")
        headline = page.select("#Terms_by_species_or_taxon").pop()
        return headline.parent.find_next_sibling("table")

    @staticmethod
    def parse_html_table(table_element: Tag) -> Dict[str, list]:
        mapping = defaultdict(list)
        for row in table_element.select("tr"):
            if Animal.is_row_an_animal(row):
                animal = Animal(row)
                for adjective in animal.collateral_adjectives:
                    mapping[adjective].append(animal.name)
        return mapping

    def __str__(self):
        representation = str()
        for col_adj, animals_list in self.__collateral_adjective_map.items():
            representation += col_adj + ": " + ", ".join(animals_list) + "\n"
        return representation


if __name__ == '__main__':
    table = AnimalsTable()
    print(table)