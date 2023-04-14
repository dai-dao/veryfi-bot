import ast
from typing import List
from typing import Optional
from pydantic import BaseModel
import jsonlines


"""
Parse function arguments using ast module
Doesn't work well enough because doesn't include type hinting info
"""
def get_function_arg(args : ast.arguments) -> List[str]:
    method_args = []
    for arg in args.args:
        method_args.append(arg.arg)
    if args.vararg is not None:
        method_args.append('*' + args.vararg.arg)
    if args.kwarg is not None:
        method_args.append('**' + args.kwarg.arg)
    return method_args


""" 
Assume that the docstring is inside the function body, as in the case with Veryfi code

Input:
    def test(a : str, b : str) -> str:
        \"\"\"
            this is docstring
        \"\"\"
        a = 1
        
Output:
    this is docstring
"""
def parse_function_docstring(function_body : str) -> Optional[str]:
    if '"""' in function_body:
        start_docstring = function_body.index('"""')
        end_docstring = function_body[start_docstring + 3 : ].index('"""')
        return function_body[start_docstring + 3 : start_docstring + 3 + end_docstring].strip().replace("  ", "")
    return None 
    

"""
- Need to use custom parsing function because using AST doesn't include type hinting 
    - Best way is to look for the opening and closing bracket of the method
- Can not parse just looking for the first closing colon ":\n" because this could occur in function type hinting
    - Also can not just look for the last occuring ":\n" either because it could be in the function body

Input:
    def test(a :
            str = '()', b : str) -> str:
        a = '''
            b :
            1
        '''
        
Output:
    def test(a :
            str = '()', b : str) -> str:
"""
def parse_function_definition(function_body : str) -> Optional[str]:
    if function_body.strip().startswith("def "):
        open_bracket_offset = function_body.index("(")
        close_bracket_offset = -1
        open_bracket_count = 1
        encounter_quote = False
        for idx, char in enumerate(function_body[open_bracket_offset + 1 : ]):
            # In the odd case that characters ( and ) appear in a string as default arguments
            if char in ["'", "\""]:
                encounter_quote = not encounter_quote                
            if char == "(" and not encounter_quote:
                open_bracket_count += 1
            elif char == ")" and not encounter_quote:
                open_bracket_count -= 1
                # Found the first matching closing bracket for the first opening bracket which is the function definition
                if open_bracket_count == 0:
                    close_bracket_offset = idx + open_bracket_offset + 1
                    break

        # Could not find corresponding closing bracket, probably syntax error
        if close_bracket_offset == -1:
            return None
        
        # Now we can find the first colon offset starting from the end of function definition 
        colon_offset = function_body[close_bracket_offset : ].index(":\n") + close_bracket_offset
        return function_body[: colon_offset + 1].strip()


class FunctionDoc(BaseModel):
    name      : str
    docstring : Optional[str]
    definition: str

    def __str__(self) -> str:
        if self.docstring:
            return f"Function name: {self.name}\nDefinition: {self.definition}\nDoc: {self.docstring}"
        else:
            return f"Function name: {self.name}\nDefinition: {self.definition}"


"""
Given the whole code content, parse for classes and methods signatures and corresponding docstring

Write parsed content to data/{title}_doc.jsonl
"""
def get_docs(program : str, title : str) -> List[FunctionDoc]:
    program_lines = program.split("\n")
    # Parse the program and generate its AST
    tree = ast.parse(program)
    # Traverse the AST and extract the class, method, and function information
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    # So we don't check this node again and don't confuse with functions outside of this class
                    subnode.__setattr__("visited", True)
                    function_name = subnode.name
                    # Take init function but not private functions
                    if "__init__" in function_name or not function_name.startswith("_"):
                        # Parse function
                        function_body = "\n".join(program_lines[subnode.lineno - 1 : subnode.end_lineno])
                        function_docstring = parse_function_docstring(function_body)
                        function_definition = parse_function_definition(function_body)
                        out.append(FunctionDoc(name = f"{class_name}.{function_name}", 
                                            docstring=function_docstring, 
                                            definition=function_definition))
            
        # If there are function definitions outside of class definition
        elif isinstance(node, ast.FunctionDef) and not getattr(node, "visited", False):
            function_name = node.name
            function_body = "\n".join(program_lines[node.lineno - 1 : node.end_lineno])
            function_docstring = parse_function_docstring(function_body)
            function_definition = parse_function_definition(function_body)
            out.append(FunctionDoc(name = function_name, 
                                    docstring=function_docstring, 
                                    definition=function_definition))

    # Save to file
    with jsonlines.open(f"data/{title}_doc.jsonl", "w") as f:
        for doc in out:
            f.write(doc.dict())

    return out