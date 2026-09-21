"""Categoria comercial: catálogo para mapeamento OpenStreetMap.

Estrutura simples que permite adicionar novas categorias com tags OSM e
regras de filtragem por nome para aumentar precisão nas buscas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class Category:
    name: str
    group: str
    primary_tags: List[Tuple[str, str]]
    secondary_tag_sets: List[List[Tuple[str, str]]]
    accept: List[str]
    ignore: List[str]

    def tag_sets(self) -> List[List[Tuple[str, str]]]:
        return [self.primary_tags] + self.secondary_tag_sets


# Catálogo estendido organizado por grupo, com tags primárias e secundárias.
CATEGORIES: List[Category] = [
    # Alimentação
    Category(
        "Restaurante",
        "Alimentação",
        [("amenity", "restaurant")],
        [[("amenity", "fast_food")], [("amenity", "cafe")]],
        ["restaurante", "restaurant", "bistrô", "bistro", "resto"],
        ["hotel", "pousada", "motel"],
    ),
    Category(
        "Pizzaria",
        "Alimentação",
        [("cuisine", "pizza")],
        [[("amenity", "restaurant")], [("amenity", "fast_food")]],
        ["pizzaria", "pizza"],
        [],
    ),
    Category(
        "Hamburgueria",
        "Alimentação",
        [("cuisine", "burger")],
        [[("amenity", "fast_food")], [("amenity", "restaurant")]],
        ["hamburguer", "hamburgueria", "burger"],
        [],
    ),
    Category(
        "Churrascaria",
        "Alimentação",
        [("cuisine", "steak_house")],
        [[("amenity", "restaurant")]],
        ["churrascaria", "steakhouse", "steak"],
        [],
    ),
    Category(
        "Sushi",
        "Alimentação",
        [("cuisine", "sushi")],
        [[("cuisine", "japanese")]],
        ["sushi"],
        [],
    ),
    Category(
        "Temakeria",
        "Alimentação",
        [("cuisine", "sushi")],
        [[("amenity", "restaurant")]],
        ["temaki", "temakeria"],
        [],
    ),
    Category(
        "Cafeteria",
        "Alimentação",
        [("amenity", "cafe")],
        [[("shop", "bakery")]],
        ["cafe", "cafeteria", "coffee"],
        [],
    ),
    Category(
        "Padaria",
        "Alimentação",
        [("shop", "bakery")],
        [[("amenity", "cafe")]],
        ["padaria", "bakery"],
        ["farmácia", "pharmacy"],
    ),
    Category(
        "Sorveteria",
        "Alimentação",
        [("shop", "ice_cream")],
        [[("shop", "confectionery")]],
        ["sorveteria", "ice cream", "gelato"],
        [],
    ),
    Category(
        "Confeitaria",
        "Alimentação",
        [("shop", "confectionery")],
        [[("shop", "bakery")]],
        ["confeitaria", "doceria"],
        [],
    ),
    Category(
        "Lanchonete",
        "Alimentação",
        [("amenity", "fast_food")],
        [[("shop", "fast_food")]],
        ["lanchonete", "fast food"],
        [],
    ),
    Category(
        "Açaiteria",
        "Alimentação",
        [("shop", "juice")],
        [[("shop", "bakery")]],
        ["açai", "acai"],
        [],
    ),
    Category(
        "Food Truck",
        "Alimentação",
        [("amenity", "fast_food")],
        [[("shop", "food_court")]],
        ["food truck", "foodtruck"],
        [],
    ),
    Category(
        "Bistrô",
        "Alimentação",
        [("amenity", "restaurant")],
        [[("amenity", "cafe")]],
        ["bistrô", "bistro"],
        [],
    ),

    # Bebidas
    Category(
        "Bar",
        "Bebidas",
        [("amenity", "bar")],
        [[("amenity", "pub")]],
        ["bar", "pub", "tavern"],
        ["hotel", "hotelaria"],
    ),
    Category(
        "Cervejaria",
        "Bebidas",
        [("shop", "brewery")],
        [[("amenity", "bar")]],
        ["cervejaria", "brewery"],
        [],
    ),

    # Beleza
    Category(
        "Barbearia",
        "Beleza",
        [("shop", "hairdresser")],
        [[("shop", "beauty")]],
        ["barbearia", "barber", "barber shop"],
        ["salão", "salon", "beauty", "estética", "clinic"],
    ),
    Category(
        "Salão de Beleza",
        "Beleza",
        [("shop", "beauty")],
        [[("shop", "hairdresser")]],
        ["salão", "salon", "beauty", "hair", "studio"],
        ["barbearia", "barber"],
    ),
    Category(
        "Clínica de Estética",
        "Beleza",
        [("healthcare", "aesthetic_clinic")],
        [[("shop", "beauty")]],
        ["estética", "aesthetic", "clinic"],
        ["barbearia", "barber"],
    ),
    Category(
        "Esmalteria",
        "Beleza",
        [("shop", "beauty")],
        [[("shop", "hairdresser")]],
        ["esmalteria", "manicure"],
        [],
    ),
    Category(
        "Designer de Sobrancelhas",
        "Beleza",
        [("shop", "beauty")],
        [],
        ["sobrancelha", "brow"],
        [],
    ),
    Category(
        "Cabeleireiro",
        "Beleza",
        [("shop", "hairdresser")],
        [[("shop", "beauty")]],
        ["cabeleireiro", "hair"],
        [],
    ),
    Category(
        "Maquiadora",
        "Beleza",
        [("shop", "beauty")],
        [],
        ["maquiador", "makeup"],
        [],
    ),
    Category(
        "Depilação",
        "Beleza",
        [("shop", "beauty")],
        [],
        ["depilação", "depilation"],
        [],
    ),

    # Saúde
    Category(
        "Dentista",
        "Saúde",
        [("amenity", "dentist")],
        [[("healthcare", "dentist")]],
        ["dentista", "dentistry", "odontologia"],
        [],
    ),
    Category(
        "Clínica Odontológica",
        "Saúde",
        [("healthcare", "dentistry")],
        [[("amenity", "dentist")]],
        ["odontologia", "clinic dentist"],
        [],
    ),
    Category(
        "Psicólogo",
        "Saúde",
        [("healthcare", "psychotherapist")],
        [],
        ["psicólogo", "psychologist"],
        [],
    ),
    Category(
        "Nutricionista",
        "Saúde",
        [("healthcare", "nutritionist")],
        [],
        ["nutricionista", "nutritionist"],
        [],
    ),
    Category(
        "Academia",
        "Saúde",
        [("leisure", "fitness_centre"), ("sport", "fitness")],
        [[("leisure", "sports_centre")]],
        ["academia", "fitness", "gym"],
        [],
    ),
    Category(
        "Farmácia",
        "Saúde",
        [("amenity", "pharmacy")],
        [[("shop", "chemist")]],
        ["farmacia", "pharmacy", "droga"],
        [],
    ),
    Category(
        "Hospital",
        "Saúde",
        [("amenity", "hospital")],
        [],
        ["hospital"],
        [],
    ),
    Category(
        "Clínica Médica",
        "Saúde",
        [("amenity", "clinic")],
        [],
        ["clínica", "clinic", "medical"],
        ["veterinary", "pet", "salão"],
    ),
    Category(
        "Laboratório",
        "Saúde",
        [("amenity", "laboratory")],
        [],
        ["lab", "laboratório", "laboratory"],
        [],
    ),
    Category(
        "Fisioterapia",
        "Saúde",
        [("healthcare", "physiotherapy")],
        [],
        ["fisioterapia", "physiotherapy"],
        [],
    ),

    # Automotivo
    Category(
        "Oficina Mecânica",
        "Automotivo",
        [("shop", "car_repair")],
        [[("shop", "car_parts")]],
        ["oficina", "mecânica", "garage", "auto repair"],
        [],
    ),
    Category(
        "Lava Rápido",
        "Automotivo",
        [("shop", "car_wash")],
        [],
        ["lava rápido", "car wash"],
        [],
    ),
    Category(
        "Borracharia",
        "Automotivo",
        [("shop", "tyres")],
        [],
        ["borracharia", "tyre", "tire"],
        [],
    ),
    Category(
        "Auto Peças",
        "Automotivo",
        [("shop", "car_parts")],
        [],
        ["autopeças", "auto partes", "auto parts"],
        [],
    ),
    Category(
        "Funilaria",
        "Automotivo",
        [("shop", "car_repair")],
        [],
        ["funilaria", "panel beater"],
        [],
    ),
    Category(
        "Auto Elétrica",
        "Automotivo",
        [("shop", "car_repair")],
        [],
        ["auto elétrica", "auto eletrica"],
        [],
    ),
    Category(
        "Concessionária",
        "Automotivo",
        [("shop", "car_dealer")],
        [],
        ["concessionaria", "dealership"],
        [],
    ),

    # Comércio
    Category(
        "Loja de Roupas",
        "Comércio",
        [("shop", "clothes")],
        [],
        ["loja", "roupas", "clothing"],
        [],
    ),
    Category(
        "Loja de Calçados",
        "Comércio",
        [("shop", "shoes")],
        [],
        ["calçados", "shoes"],
        [],
    ),
    Category(
        "Loja de Informática",
        "Comércio",
        [("shop", "computer")],
        [],
        ["informática", "computador", "computer"],
        [],
    ),
    Category(
        "Papelaria",
        "Comércio",
        [("shop", "stationery")],
        [],
        ["papelaria", "stationery"],
        [],
    ),
    Category(
        "Livraria",
        "Comércio",
        [("shop", "books")],
        [],
        ["livraria", "bookstore"],
        [],
    ),
    Category(
        "Pet Shop",
        "Comércio",
        [("shop", "pet")],
        [[("shop", "pet_supply")]],
        ["pet shop", "petshop"],
        [],
    ),
    Category(
        "Floricultura",
        "Comércio",
        [("shop", "flower")],
        [],
        ["floricultura", "flower"],
        [],
    ),
    Category(
        "Ótica",
        "Comércio",
        [("shop", "optician")],
        [],
        ["ótica", "optica", "optician"],
        [],
    ),
    Category(
        "Loja de Móveis",
        "Comércio",
        [("shop", "furniture")],
        [],
        ["móveis", "moveis", "furniture"],
        [],
    ),
    Category(
        "Eletrônicos",
        "Comércio",
        [("shop", "electronics")],
        [],
        ["eletrônicos", "electronics"],
        [],
    ),

    # Serviços
    Category(
        "Advogado",
        "Serviços",
        [("office", "lawyer")],
        [],
        ["advogado", "lawyer"],
        [],
    ),
    Category(
        "Contador",
        "Serviços",
        [("office", "accountant")],
        [],
        ["contador", "accountant"],
        [],
    ),
    Category(
        "Imobiliária",
        "Serviços",
        [("office", "real_estate_agent")],
        [[("shop", "estate_agent")]],
        ["imobiliária", "real estate"],
        [],
    ),
    Category(
        "Agência de Marketing",
        "Serviços",
        [("office", "marketing")],
        [],
        ["marketing", "agência"],
        [],
    ),
    Category(
        "Agência de Viagens",
        "Serviços",
        [("office", "travel_agent")],
        [],
        ["agência de viagens", "travel agency"],
        [],
    ),
    Category(
        "Hotel",
        "Serviços",
        [("tourism", "hotel")],
        [[("tourism", "guest_house")], [("tourism", "motel")]],
        ["hotel"],
        [],
    ),
    Category(
        "Pousada",
        "Serviços",
        [("tourism", "guest_house")],
        [],
        ["pousada", "guest house"],
        [],
    ),
    Category(
        "Lavanderia",
        "Serviços",
        [("shop", "laundry")],
        [],
        ["lavanderia", "laundry"],
        [],
    ),
    Category(
        "Escola",
        "Serviços",
        [("amenity", "school")],
        [],
        ["escola", "school"],
        [],
    ),
    Category(
        "Curso de Idiomas",
        "Serviços",
        [("amenity", "language_school")],
        [],
        ["idiomas", "language school"],
        [],
    ),
    Category(
        "Escritório de Arquitetura",
        "Serviços",
        [("office", "architect")],
        [],
        ["arquitetura", "architect"],
        [],
    ),

    # Tecnologia
    Category(
        "Desenvolvimento de Software",
        "Tecnologia",
        [("office", "software")],
        [],
        ["software", "desenvolvimento"],
        [],
    ),
    Category(
        "Consultoria de TI",
        "Tecnologia",
        [("office", "it_service")],
        [],
        ["ti", "it consulting"],
        [],
    ),

    # Transporte
    Category(
        "Táxi",
        "Transporte",
        [("amenity", "taxi")],
        [],
        ["taxi"],
        [],
    ),
    Category(
        "Transporte Executivo",
        "Transporte",
        [("office", "transport_company")],
        [],
        ["transporte"],
        [],
    ),

    # Lazer
    Category(
        "Cinema",
        "Lazer",
        [("amenity", "cinema")],
        [],
        ["cinema"],
        [],
    ),
    Category(
        "Teatro",
        "Lazer",
        [("amenity", "theatre")],
        [],
        ["teatro"],
        [],
    ),
    Category(
        "Parque",
        "Lazer",
        [("leisure", "park")],
        [],
        ["parque"],
        [],
    ),

    # Educação
    Category(
        "Creche",
        "Educação",
        [("amenity", "childcare")],
        [],
        ["creche"],
        [],
    ),
    Category(
        "Universidade",
        "Educação",
        [("amenity", "university")],
        [],
        ["universidade"],
        [],
    ),

    # Serviços financeiros
    Category(
        "Banco",
        "Financeiro",
        [("amenity", "bank")],
        [],
        ["banco"],
        [],
    ),
    Category(
        "Caixa Eletrônico",
        "Financeiro",
        [("amenity", "atm")],
        [],
        ["atm", "caixa"],
        [],
    ),

    # Mais categorias variadas para atingir ~100 entradas
    Category(
        "Spa",
        "Beleza",
        [("shop", "beauty")],
        [],
        ["spa"],
        [],
    ),
    Category(
        "Clinica Veterinária",
        "Saúde",
        [("shop", "veterinary")],
        [],
        ["veterinária", "veterinary"],
        [],
    ),
    Category(
        "Pet Grooming",
        "Comércio",
        [("shop", "pet")],
        [],
        ["groom", "tosador"],
        [],
    ),
    Category(
        "Loja de Brinquedos",
        "Comércio",
        [("shop", "toys")],
        [],
        ["brinquedo", "toys"],
        [],
    ),
    Category(
        "Academia de Dança",
        "Lazer",
        [("leisure", "dance_school")],
        [],
        ["dança", "dance"],
        [],
    ),
    Category(
        "Spin Studio",
        "Saúde",
        [("leisure", "fitness_centre")],
        [],
        ["spin"],
        [],
    ),
    Category(
        "Pilates",
        "Saúde",
        [("leisure", "fitness_centre")],
        [],
        ["pilates"],
        [],
    ),
    Category(
        "Yoga Studio",
        "Saúde",
        [("leisure", "fitness_centre")],
        [],
        ["yoga"],
        [],
    ),
    Category(
        "Coworking",
        "Serviços",
        [("office", "coworking")],
        [],
        ["coworking"],
        [],
    ),
    Category(
        "Fotógrafo",
        "Serviços",
        [("office", "photographer")],
        [],
        ["fotógrafo", "photographer"],
        [],
    ),
    Category(
        "Jardim de Infância",
        "Educação",
        [("amenity", "kindergarten")],
        [],
        ["infantil", "kindergarten"],
        [],
    ),
    Category(
        "Consultório",
        "Saúde",
        [("office", "clinic")],
        [],
        ["consultório", "consultorio"],
        [],
    ),
    Category(
        "Oficina de Costura",
        "Serviços",
        [("shop", "tailor")],
        [],
        ["costura", "tailor"],
        [],
    ),
    Category(
        "Brechó",
        "Comércio",
        [("shop", "second_hand")],
        [],
        ["brechó", "brecho", "vintage"],
        [],
    ),
    Category(
        "Casa de Câmbio",
        "Financeiro",
        [("amenity", "bureau_de_change")],
        [],
        ["câmbio", "cambio"],
        [],
    ),
]


def get_category_by_name(name: str) -> Optional[Category]:
    norm = (name or "").strip().lower()
    for cat in CATEGORIES:
        if cat.name.lower() == norm:
            return cat
    # fallback: try exact match ignoring non-alnum
    simple = ''.join(ch for ch in norm if ch.isalnum())
    for cat in CATEGORIES:
        if ''.join(ch for ch in cat.name.lower() if ch.isalnum()) == simple:
            return cat
    return None


def get_all_category_names() -> List[str]:
    return sorted({cat.name for cat in CATEGORIES})
