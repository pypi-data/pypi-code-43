import click

from ejpm.engine.context import pass_ejpm_context, EjpmContext, ENV_SH_PATH, ENV_CSH_PATH


@click.command()
@click.argument('shell_name', nargs=1, default='bash')
@pass_ejpm_context
@click.pass_context
def env(ctx, ectx, shell_name):
    """env - prints environment to run installed packages

\b
Examples:
   > ejpm env sh   # prints environments in bash and compatible way
   > ejpm env csh  # prints for CSH/TCSH syntax
   > ejpm env      # same as 'ejpm env sh'


\b
So there are 3 ways of managing environment variables

    \b
    1. Dynamically source output of 'ejpm env' command (recommended):
     > source <(ejpm env)       # for bash

    \b
    2. Save output of 'ejpm env' command to a file (can be useful):
      > ejpm env sh > your-file.sh     # bash
      > ejpm env csh> your-file.csh    # CSH/TCSH

    \b
    3. Use ejpm generated 'env.sh' and 'env.csh' files (lazy and convenient):
      > $HOME/.local/share/ejpm/env.sh    # bash and compatible
      > $HOME/.local/share/ejpm/env.csh   # for CSH/TCSH


      (!) The files are regenerated each time 'ejpm <command>' changes something in EJPM.
      If you change 'db.json' by yourself, ejpm doesn't track it automatically, so call 'ejpm env'
      to regenerate these 2 files
    """

    assert isinstance(ectx, EjpmContext)

    # check if DB file already exists
    if not ectx.db.exists():
        print("Database doesn't exist. 'env' command has nothing to do")
        return

    if not shell_name:
        shell_name = 'bash'

    if shell_name in ['csh', 'tcsh']:
        print(ectx.pm.gen_csh_env_text(ectx.db.get_active_installs()))
    else:
        print(ectx.pm.gen_bash_env_text(ectx.db.get_active_installs()))

    print("# env command also regenerated files:")
    print("# {} ".format(ectx.config[ENV_SH_PATH]))
    print("# {} ".format(ectx.config[ENV_CSH_PATH]))
    ectx.save_default_bash_environ()
    ectx.save_default_csh_environ()
