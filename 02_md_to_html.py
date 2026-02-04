import argparse
import markdown

def md_to_html(md_path, output_file=None):
    with open(md_path, 'r', encoding='utf-8') as file:
        content = file.read()

    if markdown:
        html_content = markdown.markdown(content)
    else:
        html_content = minimal_md_to_html(content)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(html_content)
    else:
        print(html_content)

def minimal_md_to_html(content):
    # Convert headings
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)

    # Convert lists
    content = re.sub(r'^\* (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'^(?:\n|^)(\s*)<li>(.+)</li>', r'\1<ul>\2</ul>', content, flags=re.MULTILINE)

    # Convert code blocks
    content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)

    return content

def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML')
    parser.add_argument('md_path', type=str, default='01_source.md', nargs='?', help='Path to the markdown file (default: 01_source.md)')
    parser.add_argument('--out', type=str, help='Output file path for HTML content')

    args = parser.parse_args()
    md_to_html(args.md_path, args.out)

if __name__ == '__main__':
    main()