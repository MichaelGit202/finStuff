import random
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from .indicators import FUNCTION_ARR_DICT as functions


DEFAULT_OPERATORS = ["+", "-", "*", "/"]

class node:
    def __init__(self, data="", left=None, right=None):
        self.fitness = 0
        self.moves = 0  # Fixed: changed from local variable to instance attribute
        self.data = data
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None

    def __repr__(self):
        if self.is_leaf():
            return str(self.data)
        return f"({self.left} {self.data} {self.right})"

    def get_indicators(self):
        indicators = set()
        if self.is_leaf():
            # Matches against string names in your configuration
            if self.data in [functions[key]["name"] for key in functions]:
                indicators.add(self.data)
        else:
            indicators.update(self.left.get_indicators())
            indicators.update(self.right.get_indicators())
        return indicators

    def calculate(self, df_row):
        if self.is_leaf():
            return float(df_row[self.data])
 
        left_val = self.left.calculate(df_row)
        right_val = self.right.calculate(df_row)
 
        if self.data == "+":
            return left_val + right_val
        elif self.data == "-":
            return left_val - right_val
        elif self.data == "*":
            return left_val * right_val
        elif self.data == "/":
            if right_val == 0:
                return 0.0
            return left_val / right_val
 
        raise ValueError(f"Unknown operator: {self.data}")

    def set_fitness(self, fitness):
        self.fitness = fitness

    # --- NEW EVOLUTION FUNCTIONS ---

    def get_all_nodes(self):
        """
        Recursively collects references to all nodes in the tree.
        Used by crossover and mutation to pick random edit points.
        """
        nodes = [self]
        if not self.is_leaf():
            if self.left:
                nodes.extend(self.left.get_all_nodes())
            if self.right:
                nodes.extend(self.right.get_all_nodes())
        return nodes

    def copy(self):
        """
        Creates a deep copy of the tree structure.
        Prevents mutations to children from altering the parent histories.
        """
        new_node = node(data=self.data)
        new_node.fitness = self.fitness
        new_node.moves = self.moves
        if self.left:
            new_node.left = self.left.copy()
        if self.right:
            new_node.right = self.right.copy()
        return new_node

    def get_diversity_multiplier(self):
        """
        Uses your category strategy rule to penalize models that pack 
        redundant styles of technical indicators together.
        """
        used_indicators = self.get_indicators()
        
        if not used_indicators:
            return 0.0  # Formula is somehow empty or has zero TIs
            
        unique_categories = set()
        
        # Cross-reference the string name back to your category lists
        for ind_name in used_indicators:
            for key, meta in functions.items():
                if meta["name"] == ind_name:
                    unique_categories.update(meta["categories"])
                    break
                    
        num_categories = len(unique_categories)
        num_total_indicators = len(used_indicators)
        
        # Calculate C / Total ratio
        return float(num_categories / num_total_indicators)


def _indicator_name_pool(functions_dict: Dict[Any, Dict[str, Any]]) -> List[str]:
    return [meta["name"] for meta in functions_dict.values()]


def build_tree(
    current_depth: int,
    max_depth: int,
    method: str = "grow",
    *,
    functions_dict: Dict[Any, Dict[str, Any]] = functions,
    operators: Sequence[str] = DEFAULT_OPERATORS,
) -> node:
    indicator_names = _indicator_name_pool(functions_dict)

    if current_depth >= max_depth:
        return node(data=random.choice(indicator_names))

    if method == "grow" and current_depth > 0 and random.random() < 0.5:
        return node(data=random.choice(indicator_names))

    root = node(data=random.choice(list(operators)))
    root.left = build_tree(
        current_depth + 1,
        max_depth,
        method,
        functions_dict=functions_dict,
        operators=operators,
    )
    root.right = build_tree(
        current_depth + 1,
        max_depth,
        method,
        functions_dict=functions_dict,
        operators=operators,
    )
    return root


def generate_random_tree(
    max_depth: int,
    *,
    method: str = "grow",
    current_depth: int = 0,
    functions_dict: Dict[Any, Dict[str, Any]] = functions,
    operators: Sequence[str] = DEFAULT_OPERATORS,
) -> node:
    indicator_names = _indicator_name_pool(functions_dict)

    if max_depth <= 0:
        return node(data=random.choice(indicator_names))

    if method == "grow" and current_depth > 0 and random.random() < 0.5:
        return node(data=random.choice(indicator_names))

    root = node(data=random.choice(list(operators)))
    root.left = generate_random_tree(
        max_depth - 1,
        method=method,
        current_depth=current_depth + 1,
        functions_dict=functions_dict,
        operators=operators,
    )
    root.right = generate_random_tree(
        max_depth - 1,
        method=method,
        current_depth=current_depth + 1,
        functions_dict=functions_dict,
        operators=operators,
    )
    return root


def tournament_selection(population: Sequence[node], tournament_size: int = 3) -> node:
    if len(population) == 0:
        raise ValueError("population must not be empty")
    if tournament_size <= 0:
        raise ValueError("tournament_size must be > 0")

    k = min(tournament_size, len(population))
    candidates = random.sample(list(population), k)
    return max(candidates, key=lambda program: program.fitness)


def crossover(parent_a: node, parent_b: node) -> Tuple[node, node]:
    child_a = parent_a.copy()
    child_b = parent_b.copy()

    nodes_a = child_a.get_all_nodes()
    nodes_b = child_b.get_all_nodes()

    target_node_a = random.choice(nodes_a)
    target_node_b = random.choice(nodes_b)

    target_node_a.data, target_node_b.data = target_node_b.data, target_node_a.data
    target_node_a.left, target_node_b.left = target_node_b.left, target_node_a.left
    target_node_a.right, target_node_b.right = target_node_b.right, target_node_a.right

    return child_a, child_b


def mutate(
    program: node,
    functions_dict: Dict[Any, Dict[str, Any]],
    operators_list: Sequence[str],
    max_depth: int = 2,
) -> node:
    mutated_program = program.copy()
    nodes = mutated_program.get_all_nodes()
    target_node = random.choice(nodes)

    indicator_names = _indicator_name_pool(functions_dict)

    if random.random() < 0.5:
        if target_node.is_leaf():
            target_node.data = random.choice(indicator_names)
        else:
            target_node.data = random.choice(list(operators_list))
    else:
        target_node.left = generate_random_tree(
            max_depth - 1,
            functions_dict=functions_dict,
            operators=operators_list,
        )
        target_node.right = generate_random_tree(
            max_depth - 1,
            functions_dict=functions_dict,
            operators=operators_list,
        )
        target_node.data = random.choice(list(operators_list))

    return mutated_program
