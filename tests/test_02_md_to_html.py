# tests/test_02_md_to_html.py
def test_convert_headings():
    content = '# Heading\n## Subheading\n### Subsubheading'
    result = convert_headings(content)
    expected = '<h1>Heading</h1><h2>Subheading</h2><h3>Subsubheading</h3>'
    self.assertEqual(result, expected)

def test_convert_lists():
    content = '* Item 1\n* Item 2'
    result = convert_lists(content)
    expected = '<li>Item 1</li><li>Item 2</li>'
    self.assertEqual(result, expected)

def test_convert_code_blocks():
    content = '```code```'
    result = convert_code_blocks(content)
    expected = '<pre><code>code</code></pre>'
    self.assertEqual(result, expected)