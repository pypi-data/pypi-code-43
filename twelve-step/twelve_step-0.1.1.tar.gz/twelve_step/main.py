from twelve_step.arguments import get_arguments
from twelve_step.exclude_packages_factory import construct_exclude_packages
from twelve_step.generate_dependencies import generate_dependencies
from twelve_step.outputs.output_factory import create_output


def main():
    arguments = get_arguments()
    should_exclude_package = construct_exclude_packages(arguments.exclude_packages)
    dependencies = generate_dependencies(arguments.project_path, should_exclude_package)
    create_output(arguments.output_file)(dependencies)


if __name__ == "__main__":
    main()
