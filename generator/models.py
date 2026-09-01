from dataclasses import dataclass, field


@dataclass
class Ingredient:
    name: str
    quantity: str = ""


@dataclass
class Step:
    action: str
    text: str
    timers: list[dict] = field(default_factory=list)
    temperatures: list[str] = field(default_factory=list)
    ingredients: list[Ingredient] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)
    plugins: dict = field(default_factory=dict)


@dataclass
class Recipe:
    slug: str
    title: str
    portions: int
    description: str
    tags: list[str]
    image: str
    steps: list[Step]
    ingredients: list[Ingredient]
    equipment: list[str]
    metadata: dict = field(default_factory=dict)

