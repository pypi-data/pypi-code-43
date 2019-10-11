import quixote
from quixote import get_context
import quixote.build.apt as apt
import quixote.fetch.gitlab as fetch
from quixote.inspection.build import gcc


@quixote.builder
def install_gcc():
    """
    Install the GCC compiler using the APT package manager.
    """
    
    apt.update()
    apt.install("gcc")


@quixote.fetcher
def fetch_delivery():
    fetch.gitlab()


@quixote.inspector
def compile_delivery():
    """
    Compile all the C files in the student delivery to make a program.
    """
    
    delivery_path = get_context()["delivery_path"]
    gcc(f"{delivery_path}/*.c").check("we cannot compile your delivery")


blueprint = quixote.Blueprint(
    name="my_is_even_demo_moulinette",
    author="don quixote",
)

