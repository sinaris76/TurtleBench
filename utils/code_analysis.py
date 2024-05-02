import ast
import astor 

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


class TurtleModifier(ast.NodeTransformer):
    def __init__(self, pen_size) -> None:
        super().__init__()
        self.pen_size = pen_size

    def visit_Import(self, node):
        # Handle import statements
        for alias in node.names:
            if alias.name == 'turtle':
                # Insert pensize and hideturtle commands for procedural usage
                pensize_command = self.create_turtle_command('turtle', 'pensize', self.pen_size)
                hideturtle_command = self.create_turtle_command('turtle', 'hideturtle')
                return [node, pensize_command, hideturtle_command]
        return node

    def visit_Assign(self, node):
        # Handle assignments
        if isinstance(node.value, ast.Call):
            # Check for Turtle object creation
            if ((isinstance(node.value.func, ast.Name) and node.value.func.id == 'Turtle') or
                (isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'Turtle')):
                turtle_var_name = node.targets[0].id
                pensize_command = self.create_turtle_command(turtle_var_name, 'pensize', self.pen_size)
                hideturtle_command = self.create_turtle_command(turtle_var_name, 'hideturtle')
                return [node, pensize_command, hideturtle_command]
        return node

    @staticmethod
    def create_turtle_command(turtle_name, command, arg=None):
        # Helper method to create a turtle command
        args = [ast.Constant(value=arg)] if arg is not None else []
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=turtle_name, ctx=ast.Load()),
                    attr=command,
                    ctx=ast.Load()
                ),
                args=args,
                keywords=[]
            )
        )


def insert_pensize_and_hideturtle(code, pen_size=5):
    tree = ast.parse(code)
    TurtleModifier(pen_size=pen_size).visit(tree)
    modified_code = astor.to_source(tree)
    return modified_code
