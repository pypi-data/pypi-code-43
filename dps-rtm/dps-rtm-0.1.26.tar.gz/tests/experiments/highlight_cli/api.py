import click


def main(highlight=False, highlight_original=False):
    click.echo("Welcome")

    if highlight_original:
        highlight_original = click.confirm('Are you sure you want to edit the original excel file? Images, etc will be lost.')

    fields = validate()
    if highlight:
        highlight_excel(fields, highlight_original)
    click.echo("Goodbye")


def validate():
    click.echo("Validating the worksheet")
    fields = list(range(5))
    click.echo("Outputting results to command line")
    return fields


def highlight_excel(fields, original):
    click.echo("Modifying excel file in-memory")
    if original:
        click.echo('Saving to original excel sheet')
    else:
        click.echo('Saving copy of original excel sheet')
