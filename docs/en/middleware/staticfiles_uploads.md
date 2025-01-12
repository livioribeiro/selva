# Static and uploaded files

The `static_files_middleware` and `uploaded_files_middleware` provide a way of serving
static content and user uploaded files.

There are two separate middlewares to allow distinct handling in the middleware
pipeline. For example, you could set the uploaded files to be served after authorization,
while the static files remain publicly accessible.

## Usage

First you need to activate the middlewares in the `settings.yaml`

```yaml
middleware:
  # ...
  - selva.web.middleware.files.static_files_middleware
  - selva.web.middleware.files.uploaded_files_middleware
  # ...
```

After that, files located in the directories `resources/static` and `resources/uploads`
will be served at `/static/` and `/uploads/`, respectively.

## Static files mappings

You can map specific paths to single static files in order to, for example, serve
the favicon at `/favicon.ico` pointing to a file in `resources/static/`:

```yaml
middleware:
  - selva.web.middleware.files.static_files_middleware
staticfiles:
  mappings:
    favicon.ico: my-icon.ico
```

## Configuration options

The available options to configure the `static_files_middleware` and `uploaded_files_middleware`
are shown below:

```yaml
staticfiles:
    path: /static # (1)
    root: resources/static # (2)
    mappings: {}

uploadedfiles:
    path: /uploads # (3)
    root: resources/uploads # (4)
```

1.  Path where static files are served
2.  Directory where static files are located
3.  Path where uploaded files are served
4.  Directory where uploaded files are located
