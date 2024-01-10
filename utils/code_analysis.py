import ast

def find_screen_variable_name(code):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Check if the right-hand side is a call to turtle.Screen()
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == 'Screen':
                    # Return the variable name (left-hand side of the assignment)
                    if isinstance(node.targets[0], ast.Name):
                        return node.targets[0].id
    return None

