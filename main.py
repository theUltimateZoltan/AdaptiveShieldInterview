import enum
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Dict
from collections import defaultdict
import requests

class Column(enum.Enum):
    ANIMAL= 0
    COLLATERAL_ADJ= 5

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
            animal_details = row.select("td")
            if len(animal_details) <= 1:
                continue  # must be a letter seperator or header row
            collateral_adjectives = animal_details[Column.COLLATERAL_ADJ.value].get_text(strip=True, separator='\n').splitlines()
            collateral_adjectives = [adj.capitalize().strip() for adj in collateral_adjectives if adj.isalpha()]  # screen redundant comments and marks
            animal_name = animal_details[Column.ANIMAL.value].text
            animal_name = animal_name.capitalize().split("(")[0].split("[")[0].split(" also see")[0].split(" see")[0].strip()
            for adjective in collateral_adjectives:
                mapping[adjective].append(animal_name)
        return mapping

    def __str__(self):
        representation = str()
        for col_adj, animals_list in self.__collateral_adjective_map.items():
            representation += col_adj + ": " + ", ".join(animals_list) + "\n"
        return representation


if __name__ == '__main__':
    table = AnimalsTable()
    print(table)