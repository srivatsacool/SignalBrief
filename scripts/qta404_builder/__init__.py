# Package init for QTA 404 notebook builder
import nbformat as nbf

def md(content):
    return nbf.v4.new_markdown_cell(content.strip())

def code(content):
    return nbf.v4.new_code_cell(content.strip())
