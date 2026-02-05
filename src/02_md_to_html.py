# src/02_md_to_html.py
import argparse
import markdown
import re
import os

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
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(html_content)
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print(html_content)

def convert_markdown_to_html_core(content):
    content = convert_headings(content)
    content = convert_lists(content)
    content = convert_code_blocks(content)
    return content