# Jinja

This extension provides support for Jinja templates.

## Usage

To use jinja templates, first install the `jinja` extra:

```shell
pip install selva[jinja]
```

Then activate the extension:

=== "configuration/settings.yaml"
    ```yaml
    extensions:
      - selva.ext.templates.jinja
    ```

You can view the template usage [in the templates section](../templates.md).

## Configuration

Jinja can be configured through the `settings.yaml`. For example, to activate extensions:

```yaml
templates:
  jinja:
    extensions:
      - jinja2.ext.i18n
      - jinja2.ext.debug
```

Full list of settings:

```yaml
templates:
  jinja:
    block_start_string: ""
    block_end_string: ""
    variable_start_string: ""
    variable_end_string: ""
    comment_start_string: ""
    comment_end_string: ""
    line_statement_prefix: ""
    line_comment_prefix: ""
    trim_blocks: true
    lstrip_blocks: true
    newline_sequence: "\n" # or "\r\n" or "\r"
    keep_trailing_newline: true
    extensions:
      - extension1
      - extensions2
    optimized: true
    undefined: "" # dotted path to python class
    finalize: "" # dotted path to python function
    autoescape: "" # dotted path to python function
    loader: "" # dotted path to python object
    cache_size: 1
    auto_reload: true
    bytecode_cache: "" # dotted path to python object
```