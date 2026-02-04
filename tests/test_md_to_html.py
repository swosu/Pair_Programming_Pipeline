import pytest
from pathlib import Path

from 02_md_to_html import md_to_html, minimal_md_to_html

def test_minimal_md_to_html_headings():
    input_markdown = "# Heading\n## Subheading\n### Sub-subheading"
    expected_output = "<h1>Heading</h1>\n<h2>Subheading</h2>\n<h3>Sub-subheading</h3>"
    assert minimal_md_to_html(input_markdown) == expected_output

def test_minimal_md_to_html_lists():
    input_markdown = "* Item 1\n* Item 2\n**Item 3**"
    expected_output = "<ul><li>Item 1</li>\n<li>Item 2</li>\n<li>Item 3</li></ul>"
    assert minimal_md_to_html(input_markdown) == expected_output

def test_minimal_md_to_html_code_blocks():
    input_markdown = "```\ndef hello_world():\n    print('Hello, World!')\n```"
    expected_output = "<pre><code>def hello_world():\n    print('Hello, World!')</code></pre>"
    assert minimal_md_to_html(input_markdown) == expected_output

@pytest.mark.parametrize("md_content, expected_html", [
    ("# Heading\n* Item 1", "<h1>Heading</h1>\n<ul><li>Item 1</li></ul>"),
    ("## Subheading\n**Item 2**", "<h2>Subheading</h2>\n<ul><li>Item 2</li></ul>")
])
def test_md_to_html_with_markdown_library(md_content, expected_html, tmp_path):
    md_file = tmp_path / "test.md"
    with open(md_file, 'w', encoding='utf-8') as file:
        file.write(md_content)

    html_file = tmp_path / "output.html"
    md_to_html(str(md_file), str(html_file))

    with open(html_file, 'r', encoding='utf-8') as file:
        assert file.read() == expected_html

@pytest.mark.parametrize("md_content, expected_html", [
    ("# Heading\n* Item 1", "<h1>Heading</h1>\n<ul><li>Item 1</li></ul>"),
    ("## Subheading\n**Item 2**", "<h2>Subheading</h2>\n<ul><li>Item 2</li></ul>")
])
def test_md_to_html_without_markdown_library(md_content, expected_html, tmp_path):
    md_file = tmp_path / "test.md"
    with open(md_file, 'w', encoding='utf-8') as file:
        file.write(md_content)

    html_file = tmp_path / "output.html"
    with patch.dict('sys.modules', {'markdown': None}):
        md_to_html(str(md_file), str(html_file))

    with open(html_file, 'r', encoding='utf-8') as file:
        assert file.read() == expected_html