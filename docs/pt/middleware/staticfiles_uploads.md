# Arquivos estáticos e uploads

Os middlewares `static_files_middleware` e `uploaded_files_middleware` provêem uma
forma de servir conteúdo estático e uploads de usuários.

Há dois middlewares separados que permitem tratamentos distintos na linha de middleware.
Por exemplo, você poderia definir que os uploads deve ser servidos após autorização,
enquanto os arquivos estáticos permanecer com acesso público.

## Utilização

Primeiro você deve ativar os middlewares no `settings.yaml`.

```yaml
middleware:
  # ...
  - selva.web.middleware.files.static_files_middleware
  - selva.web.middleware.files.uploaded_files_middleware
  # ...
```

Após isto, arquivos localizados nos diretórios `resources/static` e `resources/uploads`
serão servidos em `/static/` e `/uploads/`, respectivamente.

## Mapeamentos de arquivos estáticos

Você pode mapear caminhos específicos para um arquivo estático em particular para,
por exemplo, servir o favicon em `/favicon.ico` apontando para um arquivo em `resources/static/`:

```yaml
middleware:
  - selva.web.middleware.files.static_files_middleware
staticfiles:
  mappings:
    favicon.ico: my-icon.ico
```

## Configurações

As opções disponíveis para configurar `static_files_middleware` e `uploaded_files_middleware`
são mostradas abaixo:

```yaml
staticfiles:
    path: /static # (1)
    root: resources/static # (2)
    mappings: {}

uploadedfiles:
    path: /uploads # (3)
    root: resources/uploads # (4)
```

1.  Caminho onde os arquivos estáticos são servidos
2.  Diretório onde os arquivos estáticos são localizados
3.  Caminho onde os uploads são servidos
4.  Diretório onde os uploads são localizados
