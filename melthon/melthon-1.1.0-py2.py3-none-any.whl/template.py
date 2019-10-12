import tempfile
from pathlib import Path

from mako.lookup import TemplateLookup


def render_templates(templates_path, output_path, context, pretty_urls):
    with tempfile.TemporaryDirectory() as tmp_dir:
        template_lookup = TemplateLookup(directories=[templates_path],
                                         module_directory=tmp_dir,
                                         output_encoding='utf-8',
                                         encoding_errors='replace')

        # For each .mako template
        for template_path in templates_path.rglob('*.mako'):
            # Remove base directory name
            template_path = Path(*template_path.parts[1:])

            # Check for ignored files: <PAGE NAME>.template.mako and <PAGE NAME>.part.mako
            ignored_extensions = ['.template', '.part']
            if len(template_path.suffixes) >= 2 and template_path.suffixes[-2] in ignored_extensions:
                # Skip file
                continue

            # Read template
            template = template_lookup.get_template(str(template_path))

            # Determine subdir and page paths
            is_status_page = False
            try:
                status = int(template_path.stem)
                is_status_page = (400 <= status < 600)
            except ValueError:
                pass

            if pretty_urls and template_path.stem != 'index' and not is_status_page:
                # Create pretty url
                output_subdir = output_path / template_path.parent / template_path.stem
                output_page = output_subdir / 'index.html'
            else:
                # Don't create pretty url
                output_subdir = output_path / template_path.parent
                output_page = (output_subdir / template_path.stem).with_suffix('.html')

            # Create output subdirectory
            output_subdir.mkdir(parents=True, exist_ok=True)

            # Render template
            with output_page.open('wb') as rendered_page:
                rendered_page.write(template.render(**context))
