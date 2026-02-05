# src/02_md_to_html.py
import argparse
import markdown
import re

def convert_markdown_to_html(markdown_path, output_file=None):
    try:
        with open(markdown_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found: {markdown_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    html_content = convert_markdown_to_html_core(content)

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(html_content)
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print(html_content)

def convert_markdown_to_html_core(content):
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
    parser.add_argument('markdown_path', type=str, default='01_source.md', nargs='?', help='Path to the markdown file (default: 01_source.md)')
    parser.add_argument('--out', type=str, help='Output file path for HTML content')

    args = parser.parse_args()
    convert_markdown_to_html(args.markdown_path, args.out)

if __name__ == '__main__':
    main()