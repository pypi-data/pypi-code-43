from pyfiglet import figlet_format
from colorama import Fore, Back, Style
from bullet import Bullet, SlidePrompt, Check, Input, YesNo, Numbers,colors
import click, codecs, os.path, re, time
from .utils import printProgressBar, find_version

print(Fore.BLUE + figlet_format("Breeze CLI", font="slant"))
print(Style.RESET_ALL)

version = find_version("../breezecli", "__init__.py")
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
# @click.option('--host',prompt='Enter env host name', help='Login host... E.g crm.xiaoshouyi.com')
# @click.option('--email', prompt='Enter email/username', help='Login email... E.g test@126.com')
# @click.password_option('--password',prompt='Enter password',help='Login password... E.g 123456')
@click.option('--host',help='Login host... E.g crm.xiaoshouyi.com')
@click.option('--email',help='Login email... E.g test@126.com')
@click.password_option('--password',prompt=False,help='Login password... E.g 123456')
@click.option('--tenant',prompt=False,help='Which tenant login E.g tenant123')
@click.version_option(message="breeze-cli/%s"%version)
@click.pass_context
def cli(ctx, host, email, password,tenant):
    """
    Breeze CLI to help you eailsy operate breeze data...
    """
    ctx.obj = {}
    # ctx.obj["host"] = host
    # ctx.obj["email"] = email
    # ctx.obj["password"] = password
    ctx.obj["selectedTenant"] = tenant
    if tenant_login(host,email,password,tenant):
        ctx.obj["logined"] = True
    else:
        ctx.obj["logined"] = False


@cli.command()
@click.option('--meta_path',required=True, type=str, help='Provide local meta folder to upload')
@click.pass_context
def upload_meta(ctx,meta_path):
    """
    Upload meta to CFS
    """
    if not ctx.obj["logined"]:
        click.echo(click.style('Need login first', fg='red'))
        selectedTenant = login_prompt_handle()
    else:
        selectedTenant = ctx.obj["selectedTenant"]
    isUpload = YesNo("Confirm upload meta files to %s?"%selectedTenant).launch()
    if isUpload:
        # A List of Items
        fileList = ["test1.json","form.json","bar.json"]
        for file in fileList:
            items = list(range(0, 10))
            l = len(items)

            # Initial call to print 0% progress
            printProgressBar(0, l, prefix = '上传%s:'%file, suffix = 'Complete', length = 50)
            for i, item in enumerate(items):
                # Do stuff...
                time.sleep(0.1)
                # Update Progress Bar
                printProgressBar(i + 1, l, prefix = '上传%s:'%file, suffix = 'Complete', length = 50)

        click.echo(click.style('总共上传了%s个meta文件到%s'%(len(fileList),selectedTenant), fg='green'))

@cli.command()
@click.option('--store_path', type=str, help='Provide local path for storing the downloaded meta files')
@click.pass_context
def download_meta(ctx,store_path):
    """
    Download meta from CFS
    """
    print("xxx")
    print(store_path)
 

def login_prompt_handle():
    
    host = click.prompt('Enter env host name', type=str)
    email = click.prompt('Enter email/username', type=str)
    password = click.prompt('Enter password', confirmation_prompt=True, hide_input=True,type=str),
    tenantList = Bullet(
        prompt = "Choose tenant:",
        choices = ["销售易租户1", "租户2", "租户3"], 
        indent = 0,
        align = 5, 
        margin = 2,
        shift = 0,
        bullet = "",
        pad_right = 5
    )
    selectedTenant = tenantList.launch()
    return selectedTenant

def tenant_login(host,email,password,tenant):
    if all([host,email,password,tenant]):
        return True
    else:
        return False



if __name__ == "__main__":
    cli()