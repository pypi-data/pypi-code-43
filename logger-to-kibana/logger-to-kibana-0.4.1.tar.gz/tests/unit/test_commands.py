import src.commands as commands
from unittest.mock import patch
from pytest import mark


@patch.object(commands, "get_folder_name")
@patch.object(commands.kib, "generate_folder_visualizations")
@patch.object(commands.processor, "process_folder")
@mark.parametrize(
    "folder, process_expected, generate_expected",
    [
        ("one", 1, 1),
        (None, 1, 1),
    ]
)
def test_process_and_generate_visualizations(
        process_folder, generate_folder_visualizations, get_folder_name,
        folder, process_expected, generate_expected):
    commands.process_and_generate_visualizations(folder)
    assert process_folder.call_count == process_expected
    assert generate_folder_visualizations.call_count == generate_expected
    assert get_folder_name.call_count == 1


@patch.object(commands, "get_folder_name")
@patch.object(commands.kib, "generate_and_send_visualizations")
@patch.object(commands.processor, "process_folder")
@mark.parametrize(
    "folder, process_expected, generate_expected",
    [
        ("one", 1, 1),
        (None, 1, 1),
    ]
)
def test_process_generate_and_send_visualizations(
        process_folder, generate_and_send_visualizations, get_folder_name,
        folder, process_expected, generate_expected):
    commands.process_generate_and_send_visualizations(folder)
    assert process_folder.call_count == process_expected
    assert generate_and_send_visualizations.call_count == generate_expected
    assert get_folder_name.call_count == 1


@mark.parametrize(
    "folder, expected",
    [
        ("one", "one"),
        ("/", "/"),
        ("/bla/ble", "ble"),
        ("/bla/ble/bli", "bli"),
    ]
)
def test_get_folder_name(folder, expected):
    assert commands.get_folder_name(folder) == expected


# # # #
# # # Probably make this the "integration test"
# # # #

# # class TestCommands(unittest.TestCase):

# #     def test_command_is_command(self):
# # Test it with this http://click.palletsprojects.com/en/5.x/testing/
# #

# # if __name__ == '__name__':
# #     unittest.main()
