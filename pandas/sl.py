import random

from faker import Faker

fake = Faker()
Faker.seed(1212)


class Entity:

    def __init__(
        self, uid, entity_type, entity_name, location, address, phone, shortcut
    ):
        self.uid = uid
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.location = location
        self.address = address
        self.phone = phone
        self.shortcut = shortcut

    def __repr__(self):
        return f"Entity(uid={self.uid}, entity_type={self.entity_type}, entity_name={self.entity_name}, location={self.location}, address={self.address}, phone={self.phone}, shortcut={self.shortcut})"


def generate_entities(num_entities):
    entities = []
    for _ in range(num_entities):
        uid = fake.user_name()
        entity_type = fake.random_element(
            elements=(
                "Individual",
                "Asset Management",
                "Brokerage",
                "Bank",
                "Crypto Exchange",
                "Insurance",
                "Employment",
                "Custodian",
                "Government",
                "Family Office",
                "Private Equity",
            )
        )
        if entity_type == "Individual":
            entity_name = fake.name()
        elif entity_type == "Government":
            entity_name = fake.company_suffix()
        else:
            entity_name = fake.company()
        location = fake.random_element(
            elements=(
                "US",
                "India",
                "Hong Kong",
                "Australia",
                "Singapore",
                "UK",
                "Japan",
                "Switzerland",
                "Jersey",
                "Man Of Isle",
                "Scotland",
            )
        )
        address = fake.address()
        phone = fake.phone_number()
        shortcut = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        entities.append(
            Entity(
                uid, entity_type, entity_name, location, address, phone,
                shortcut
            )
        )
    return entities


# Generate 10 random entities
entities = generate_entities(50)

# Print the generated entities
for entity in entities:
    print(entity)
