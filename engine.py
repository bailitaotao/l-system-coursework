"""L-System geometry. Uses ordinary coordinates, with positive y pointing up."""
from dataclasses import dataclass
import json
from math import cos, sin, radians, isfinite
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent / "configs"
FILES = ("01-plant-a", "02-plant-b", "03-plant-c", "04-plant-d",
         "05-plant-e", "06-plant-f", "07-koch", "08-dragon")
PAPER = "#faf8ef"
INK = "#233e34"
DEPTH_COLORS = ("#584432", "#70523b", "#5c6845", "#3e7354", "#267657", "#238163")


@dataclass(frozen=True)
class Model:
    name: str
    axiom: str
    rules: dict
    angle: float
    length: float
    heading: float
    generation: int
    source: str


def load_model(slot):
    path = CONFIG_DIR / (FILES[slot] + ".json")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("The file must contain a JSON object.")
    model = Model(**data)
    if not isinstance(model.name, str) or not isinstance(model.source, str):
        raise ValueError("Name and source must be text.")
    if not isinstance(model.rules, dict) or any(len(k) != 1 or not k.isalpha() for k in model.rules):
        raise ValueError("Each rule needs a single letter on its left side.")
    for word in [model.axiom, *model.rules.values()]:
        if not isinstance(word, str) or len(word) > 256:
            raise ValueError("Use a string of at most 256 symbols per rule.")
        nesting = 0
        for symbol in word:
            if not (symbol.isalpha() or symbol in "+-[]"):
                raise ValueError("Use letters, +, -, [ and ].")
            nesting += (symbol == "[") - (symbol == "]")
            if nesting < 0:
                raise ValueError("A closing bracket has no matching opening bracket.")
        if nesting:
            raise ValueError("Brackets must be balanced.")
    if type(model.generation) is not int or not 0 <= model.generation <= 12:
        raise ValueError("Choose a reference generation between 0 and 12.")
    for value, low, high in [(model.angle, 0, 180), (model.length, 0.5, 20), (model.heading, 0, 360)]:
        if type(value) not in (int, float) or not isfinite(value) or not low <= value <= high:
            raise ValueError("Angle, step length or heading is outside its range.")
    return model


def expand(axiom, rules, generation):
    """和入门 demo 一样，每一代都从上一代的完整字符串生成。"""
    word = axiom
    for _ in range(generation):
        parts = [rules.get(symbol, symbol) for symbol in word]
        if sum(map(len, parts)) > 200_000:
            raise ValueError("This generation exceeds 200,000 symbols. Reduce the reference generation.")
        word = "".join(parts)
    return word


def trace(word, angle, length, heading):
    """F draws. Brackets save and restore the turtle. Other letters stay invisible."""
    x = y = 0.0
    stack = []
    segments = []
    for symbol in word:
        if symbol == "F":
            direction = radians(heading)
            nx, ny = x + length * cos(direction), y + length * sin(direction)
            segments.append((x, y, nx, ny, len(stack)))
            x, y = nx, ny
        elif symbol == "+":
            heading += angle
        elif symbol == "-":
            heading -= angle
        elif symbol == "[":
            stack.append((x, y, heading))
        elif symbol == "]":
            x, y, heading = stack.pop()
    return segments


def bounds(segments):
    left = right = bottom = top = 0.0
    for x, y, nx, ny, _ in segments:
        left, right = min(left, x, nx), max(right, x, nx)
        bottom, top = min(bottom, y, ny), max(top, y, ny)
    return left, bottom, right, top


class Specimen:
    """One file and the user's current drawing settings."""
    def __init__(self, slot):
        self.model = m = load_model(slot)
        self.slot = slot
        self.generation = m.generation
        self.angle, self.length, self.heading = m.angle, m.length, m.heading
        self.words = {}
        self.reference = bounds(self.segments())

    def segments(self):
        if self.generation not in self.words:
            self.words[self.generation] = expand(self.model.axiom, self.model.rules, self.generation)
        return trace(self.words[self.generation], self.angle, self.length, self.heading)

    def adjust(self, key, sign):
        limits = {"generation": (1, 0, self.model.generation), "angle": (2.5, 0, 180),
                  "length": (0.5, 0.5, 20), "heading": (5, 0, 360)}
        step, lo, hi = limits[key]
        setattr(self, key, max(lo, min(hi, round(getattr(self, key) + sign * step, 2))))


def project(segments, reference, width, height, fit=False):
    """Use the reference scale across generations. Fit explicitly to reframe extremes."""
    x0, y0, x1, y1 = bounds(segments)
    left, bottom, right, top = (x0, y0, x1, y1) if fit else reference
    scale = min(width * .85 / max(right-left, 1), height * .83 / max(top-bottom, 1))
    cx, cy = (x0+x1)/2, (y0+y1)/2
    return [(width/2+(x-cx)*scale, height/2-(y-cy)*scale,
             width/2+(nx-cx)*scale, height/2-(ny-cy)*scale, depth)
            for x, y, nx, ny, depth in segments]


def stroke(depth, color):
    return DEPTH_COLORS[min(depth, len(DEPTH_COLORS)-1)] if color else INK
