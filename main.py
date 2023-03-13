import enum
import os.path
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Dict, Union, List, Set
from collections import defaultdict
import requests
import shutil
from threading import Thread
from copy import copy

class Column(enum.Enum):
    ANIMAL= 0
    COLLATERAL_ADJ= 5

WIKIPEDIA = "https://en.wikipedia.org/"

class Animal:
    def __init__(self, row: Tag):
        self.image_local_path = None

        if not Animal.is_row_an_animal(row):
            raise ValueError("Row does not represent an animal")

        details = Animal.extract_details_from_row(row)
        unprocessed_collaterals = details[Column.COLLATERAL_ADJ.value].get_text(strip=True,
                                                                                     separator='\n').splitlines()
        self.collateral_adjectives = Animal.process_collateral_adjectives(unprocessed_collaterals)
        unprocessed_name = details[Column.ANIMAL.value].text
        self.name = Animal.process_name(unprocessed_name)
        self.link = WIKIPEDIA + details[Column.ANIMAL.value].find("a")["href"]
        self.image_finder = Thread(target=self.__find_image_details)
        self.image_finder.start()

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
        exit_phrases = ["(", "[", "also see", " see"]
        stripped_name = copy(name).capitalize()
        for exit_phrase in exit_phrases:
            stripped_name = stripped_name.split(exit_phrase)[0]
        return stripped_name.strip()

    @staticmethod
    def process_collateral_adjectives(adjectives: List[str]) -> List[str]:
        return [adj.capitalize().strip() for adj in adjectives if adj.isalpha()]  # screen redundant comments and marks

    def __find_image_details(self):
        page_html = requests.get(self.link).content
        page = BeautifulSoup(page_html, features="html.parser")
        image_base_element = page.find("table", class_="infobox")
        if not image_base_element:
            image_base_element = page.find("div", class_="thumb")
        if image_base_element:
            self.image_url = "https:" + image_base_element.find("img")["src"]
            image_suffix = self.image_url.split(".")[-1]
            self.image_local_path = f'/tmp/{self.name.split("/")[0].replace(" ", "_")}.{image_suffix}'

    def download_image(self):
        self.image_finder.join()
        Animal.download_any_binary(self.image_url, self.image_local_path)

    @staticmethod
    def download_any_binary(url: str, local_path: str, use_cached=True):
        if use_cached and os.path.exists(local_path):
            return
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)


class AnimalsTable:
    def __init__(self):
        self.__table_element = AnimalsTable.get_animals_table_element()
        self.__collateral_adjective_map = AnimalsTable.parse_html_table(self.__table_element)

    @staticmethod
    def get_animals_table_element() -> Tag:
        page_html = requests.get(WIKIPEDIA + "/wiki/List_of_animal_names").content
        page = BeautifulSoup(page_html, features="html.parser")
        headline = page.select("#Terms_by_species_or_taxon").pop()
        return headline.parent.find_next_sibling("table")

    @staticmethod
    def parse_html_table(table_element: Tag) -> Dict[str, List[Animal]]:
        mapping = defaultdict(list)
        for row in table_element.select("tr"):
            if Animal.is_row_an_animal(row):
                animal = Animal(row)
                for adjective in animal.collateral_adjectives:
                    mapping[adjective].append(animal)

        return mapping

    def animals_set(self) -> Set[Animal]:
        return set().union(*[set(animals) for animals in self.__collateral_adjective_map.values()])

    def download_images(self):
        for animal in self.animals_set():
            animal.download_image()

    def get_wiki_table_row(self, index: int) -> Tag:
        return self.__table_element.find_all("tr")[index]

    def __str__(self):
        representation = str()
        for col_adj, animals_list in self.__collateral_adjective_map.items():
            animal_items = list()
            for animal in animals_list:
                animal.image_finder.join()
                animal_items.append(f"{animal.name} [ file://{animal.image_local_path} ]")
            representation += col_adj + ": " + ", ".join(animal_items) + "\n"
        return representation


if __name__ == '__main__':
    table = AnimalsTable()
    print(table)
    print("Please wait while images are being downloaded...")
    table.download_images()
    print("Images downloaded.")