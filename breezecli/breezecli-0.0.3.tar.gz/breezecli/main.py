from pyfiglet import figlet_format
from colorama import Fore, Back, Style
from bullet import Bullet, SlidePrompt, Check, Input, YesNo, Numbers
import click


print(Fore.BLUE + figlet_format("Breeze CLI", font="slant"))
print(Style.RESET_ALL)

@click.group()
@click.option('--host', prompt='env host', required=True,help='Login host... E.g crm.xiaoshouyi.com')
@click.option('--email',prompt='email', required=True,help='Login email... E.g test@126.com')
@click.option('--password',prompt='password',required=True,help='Login password... E.g 123456')
@click.pass_context
def cli(ctx=None, host= '', email= '', password= ''):
    """
    Breeze CLI to help you eailsy operate breeze dataff...
    """
    
    ctx.obj = {}
    ctx.obj["host"] = host
    ctx.obj["email"] = email
    ctx.obj["password"] = password

@cli.command()
@click.option('--meta_path',required=True, type=str, help='Provide local meta folder to upload')
@click.pass_context
def upload_meta(ctx,meta_path):
    print("xxx")

    print(ctx.obj["host"])
    print(meta_path)



if __name__ == "__main__":
    cli()