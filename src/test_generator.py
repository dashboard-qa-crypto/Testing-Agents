"""Intelligent test case generator for automatic test creation."""

import ast
import inspect
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Information about a function that needs testing."""

    name: str
    module: str
    file_path: str
    line_number: int
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    is_method: bool
    class_name: Optional[str]
    has_tests: bool = False
    complexity: int = 1


@dataclass
class TestCaseSuggestion:
    """A suggested test case."""

    function_name: str
    test_name: str
    test_type: str  # 'basic', 'edge_case', 'error', 'parametrized'
    description: str
    template: str
    priority: int  # 1-5, higher is more important


class TestCaseGenerator:
    """Generates test cases based on code analysis."""

    def __init__(self, source_dir: str = "src", test_dir: str = "tests"):
        """Initialize the test case generator.

        Args:
            source_dir: Directory containing source code
            test_dir: Directory containing test files
        """
        self.source_dir = Path(source_dir)
        self.test_dir = Path(test_dir)
        self.functions: List[FunctionInfo] = []
        self.test_suggestions: List[TestCaseSuggestion] = []

    def analyze_source_code(self) -> List[FunctionInfo]:
        """Analyze source code to find functions needing tests.

        Returns:
            List of FunctionInfo objects
        """
        self.functions = []

        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue

            try:
                with open(py_file, "r") as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                self._extract_functions(tree, py_file)
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")

        return self.functions

    def _extract_functions(self, tree: ast.AST, file_path: Path) -> None:
        """Extract function information from AST.

        Args:
            tree: AST tree
            file_path: Path to the source file
        """
        module_name = self._get_module_name(file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions unless they're important
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                func_info = FunctionInfo(
                    name=node.name,
                    module=module_name,
                    file_path=str(file_path),
                    line_number=node.lineno,
                    args=self._get_function_args(node),
                    return_type=self._get_return_type(node),
                    docstring=ast.get_docstring(node),
                    is_method=self._is_method(node),
                    class_name=self._get_class_name(node, tree),
                    complexity=self._calculate_complexity(node),
                )

                self.functions.append(func_info)

            elif isinstance(node, ast.ClassDef):
                # Process methods in classes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith("_") and not item.name.startswith("__"):
                            continue

                        func_info = FunctionInfo(
                            name=item.name,
                            module=module_name,
                            file_path=str(file_path),
                            line_number=item.lineno,
                            args=self._get_function_args(item),
                            return_type=self._get_return_type(item),
                            docstring=ast.get_docstring(item),
                            is_method=True,
                            class_name=node.name,
                            complexity=self._calculate_complexity(item),
                        )

                        self.functions.append(func_info)

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        relative_path = file_path.relative_to(self.source_dir.parent)
        return str(relative_path.with_suffix("")).replace("/", ".")

    def _get_function_args(self, node: ast.FunctionDef) -> List[str]:
        """Extract function arguments."""
        args = []
        for arg in node.args.args:
            if arg.arg != "self" and arg.arg != "cls":
                args.append(arg.arg)
        return args

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Get return type annotation if present."""
        if node.returns:
            return ast.unparse(node.returns)
        return None

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a method."""
        if node.args.args:
            first_arg = node.args.args[0].arg
            return first_arg in ("self", "cls")
        return False

    def _get_class_name(self, node: ast.FunctionDef, tree: ast.AST) -> Optional[str]:
        """Get the class name if the function is a method."""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for child in parent.body:
                    if child == node:
                        return parent.name
        return None

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    def identify_missing_tests(self) -> List[FunctionInfo]:
        """Identify functions that don't have tests.

        Returns:
            List of functions without tests
        """
        # Get all existing test functions
        existing_tests = self._get_existing_tests()

        missing_tests = []
        for func in self.functions:
            # Check if tests exist for this function
            test_pattern = f"test_{func.name}"
            if not any(test_pattern in test_name for test_name in existing_tests):
                func.has_tests = False
                missing_tests.append(func)
            else:
                func.has_tests = True

        return missing_tests

    def _get_existing_tests(self) -> Set[str]:
        """Get all existing test function names."""
        test_names = set()

        if not self.test_dir.exists():
            return test_names

        for test_file in self.test_dir.rglob("test_*.py"):
            try:
                with open(test_file, "r") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name.startswith("test_"):
                            test_names.add(node.name)
            except Exception:
                pass

        return test_names

    def generate_test_suggestions(
        self, missing_tests: Optional[List[FunctionInfo]] = None
    ) -> List[TestCaseSuggestion]:
        """Generate test case suggestions for functions.

        Args:
            missing_tests: List of functions without tests. If None, uses all functions.

        Returns:
            List of test case suggestions
        """
        if missing_tests is None:
            missing_tests = self.identify_missing_tests()

        self.test_suggestions = []

        for func in missing_tests:
            # Generate basic test
            self.test_suggestions.append(self._generate_basic_test(func))

            # Generate edge case tests
            self.test_suggestions.extend(self._generate_edge_case_tests(func))

            # Generate error tests
            self.test_suggestions.extend(self._generate_error_tests(func))

            # Generate parametrized tests if applicable
            if len(func.args) > 0:
                self.test_suggestions.append(self._generate_parametrized_test(func))

        return self.test_suggestions

    def _generate_basic_test(self, func: FunctionInfo) -> TestCaseSuggestion:
        """Generate a basic test case."""
        test_name = f"test_{func.name}_basic"

        if func.is_method and func.class_name:
            template = f'''def {test_name}(self):
    """Test basic functionality of {func.class_name}.{func.name}."""
    # Arrange
    obj = {func.class_name}()

    # Act
    result = obj.{func.name}({self._generate_sample_args(func.args)})

    # Assert
    assert result is not None
    # TODO: Add specific assertions
'''
        else:
            template = f'''def {test_name}():
    """Test basic functionality of {func.name}."""
    # Arrange
    {self._generate_setup_code(func.args)}

    # Act
    result = {func.name}({self._generate_sample_args(func.args)})

    # Assert
    assert result is not None
    # TODO: Add specific assertions
'''

        return TestCaseSuggestion(
            function_name=func.name,
            test_name=test_name,
            test_type="basic",
            description=f"Basic functionality test for {func.name}",
            template=template,
            priority=5,
        )

    def _generate_edge_case_tests(self, func: FunctionInfo) -> List[TestCaseSuggestion]:
        """Generate edge case tests."""
        suggestions = []

        # Common edge cases based on argument types
        edge_cases = {
            "empty": ("empty input", ["", [], {}, None]),
            "zero": ("zero value", [0, 0.0]),
            "negative": ("negative value", [-1, -100]),
            "large": ("large value", [999999, 1e10]),
            "none": ("None value", [None]),
        }

        if func.args:
            for case_name, (description, values) in edge_cases.items():
                test_name = f"test_{func.name}_{case_name}"
                template = f'''def {test_name}():
    """Test {func.name} with {description}."""
    # Test with {description}
    # TODO: Implement test for {case_name} case
    pass
'''
                suggestions.append(
                    TestCaseSuggestion(
                        function_name=func.name,
                        test_name=test_name,
                        test_type="edge_case",
                        description=f"Edge case: {description}",
                        template=template,
                        priority=3,
                    )
                )

        return suggestions[:2]  # Limit to 2 most important edge cases

    def _generate_error_tests(self, func: FunctionInfo) -> List[TestCaseSuggestion]:
        """Generate error handling tests."""
        suggestions = []

        if func.args:
            test_name = f"test_{func.name}_invalid_input"
            template = f'''def {test_name}():
    """Test {func.name} with invalid input."""
    with pytest.raises(Exception):  # TODO: Specify exact exception
        {func.name}(invalid_input)
'''
            suggestions.append(
                TestCaseSuggestion(
                    function_name=func.name,
                    test_name=test_name,
                    test_type="error",
                    description="Test error handling with invalid input",
                    template=template,
                    priority=4,
                )
            )

        return suggestions

    def _generate_parametrized_test(self, func: FunctionInfo) -> TestCaseSuggestion:
        """Generate parametrized test."""
        test_name = f"test_{func.name}_parametrized"

        args_str = ", ".join(func.args)
        template = f'''@pytest.mark.parametrize("{args_str}, expected", [
    # TODO: Add test cases
    # (input1, input2, expected_output),
])
def {test_name}({args_str}, expected):
    """Parametrized test for {func.name}."""
    result = {func.name}({args_str})
    assert result == expected
'''

        return TestCaseSuggestion(
            function_name=func.name,
            test_name=test_name,
            test_type="parametrized",
            description="Parametrized test with multiple inputs",
            template=template,
            priority=4,
        )

    def _generate_sample_args(self, args: List[str]) -> str:
        """Generate sample argument values."""
        if not args:
            return ""

        samples = []
        for arg in args:
            if "count" in arg.lower() or "num" in arg.lower():
                samples.append("10")
            elif "name" in arg.lower() or "str" in arg.lower():
                samples.append('"test"')
            elif "path" in arg.lower():
                samples.append('"test/path"')
            elif "flag" in arg.lower() or "is_" in arg.lower():
                samples.append("True")
            else:
                samples.append("test_value")

        return ", ".join(samples)

    def _generate_setup_code(self, args: List[str]) -> str:
        """Generate setup code for test."""
        if not args:
            return "# No setup needed"

        setup_lines = []
        for arg in args:
            setup_lines.append(f"{arg} = None  # TODO: Set test value")

        return "\n    ".join(setup_lines)

    def create_test_file(
        self, func: FunctionInfo, suggestions: List[TestCaseSuggestion]
    ) -> str:
        """Create a complete test file for a module.

        Args:
            func: Function information
            suggestions: List of test suggestions

        Returns:
            Complete test file content
        """
        module_path = func.module.replace(".", "/")
        imports = f"""\"\"\"Tests for {func.module}.\"\"\"

import pytest
from {func.module} import {func.class_name or func.name}


"""

        if func.class_name:
            class_tests = f"""class Test{func.class_name}:
    \"\"\"Test cases for {func.class_name}.\"\"\"

"""
            for suggestion in suggestions:
                # Indent the template
                indented_template = "\n".join(
                    "    " + line for line in suggestion.template.split("\n")
                )
                class_tests += indented_template + "\n"

            return imports + class_tests
        else:
            tests = imports
            for suggestion in suggestions:
                tests += suggestion.template + "\n\n"
            return tests

    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate a report on test coverage gaps.

        Returns:
            Dictionary with coverage gap information
        """
        missing_tests = self.identify_missing_tests()

        report = {
            "total_functions": len(self.functions),
            "tested_functions": len(self.functions) - len(missing_tests),
            "untested_functions": len(missing_tests),
            "coverage_percentage": (
                (len(self.functions) - len(missing_tests)) / len(self.functions) * 100
                if self.functions
                else 0
            ),
            "missing_by_module": {},
            "missing_by_complexity": {"low": 0, "medium": 0, "high": 0},
        }

        for func in missing_tests:
            # Group by module
            if func.module not in report["missing_by_module"]:
                report["missing_by_module"][func.module] = []
            report["missing_by_module"][func.module].append(func.name)

            # Group by complexity
            if func.complexity <= 2:
                report["missing_by_complexity"]["low"] += 1
            elif func.complexity <= 5:
                report["missing_by_complexity"]["medium"] += 1
            else:
                report["missing_by_complexity"]["high"] += 1

        return report

    def save_test_suggestions(self, output_file: str = "test_suggestions.md") -> None:
        """Save test suggestions to a markdown file.

        Args:
            output_file: Path to output file
        """
        content = "# Test Case Suggestions\n\n"
        content += f"Generated {len(self.test_suggestions)} test suggestions\n\n"

        # Group by function
        by_function: Dict[str, List[TestCaseSuggestion]] = {}
        for suggestion in self.test_suggestions:
            if suggestion.function_name not in by_function:
                by_function[suggestion.function_name] = []
            by_function[suggestion.function_name].append(suggestion)

        for func_name, suggestions in by_function.items():
            content += f"\n## {func_name}\n\n"

            # Sort by priority
            suggestions.sort(key=lambda x: x.priority, reverse=True)

            for suggestion in suggestions:
                content += f"### {suggestion.test_name} (Priority: {suggestion.priority})\n\n"
                content += f"**Type:** {suggestion.test_type}\n\n"
                content += f"**Description:** {suggestion.description}\n\n"
                content += "```python\n"
                content += suggestion.template
                content += "```\n\n"

        with open(output_file, "w") as f:
            f.write(content)
