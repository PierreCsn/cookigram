from dataclasses import dataclass, field


@dataclass
class Ingredient:
    name: str
    quantity: str = ""
    icon: str = ""


@dataclass
class ParallelOperation:
    id: str
    label: str
    text: str
    timers: list[dict] = field(default_factory=list)
    temperatures: list[str] = field(default_factory=list)
    ingredients: list[Ingredient] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)


@dataclass
class Step:
    id: str
    action: str
    text: str
    timers: list[dict] = field(default_factory=list)
    temperatures: list[str] = field(default_factory=list)
    ingredients: list[Ingredient] = field(default_factory=list)
    equipment: list[str] = field(default_factory=list)
    substeps: list[str] = field(default_factory=list)
    parallel: list[ParallelOperation] = field(default_factory=list)
    plugins: dict = field(default_factory=dict)


@dataclass
class RecipeVariant:
    id: str
    name: str
    description: str
    default: bool
    steps: list[Step]
    ingredients: list[Ingredient]
    equipment: list[str]
    prep_time: str
    total_time: str
    appliances: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    nutrition: dict = field(default_factory=dict)
    shopping: dict = field(default_factory=dict)


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
    prep_time: str = ""
    total_time: str = ""
    scalable: bool = True
    min_portions: int = 1
    max_portions: int = 12
    portion_step: int = 1
    scaling_note: str = ""
    nutrition: dict = field(default_factory=dict)
    shopping: dict = field(default_factory=dict)
    variants: list[RecipeVariant] = field(default_factory=list)
