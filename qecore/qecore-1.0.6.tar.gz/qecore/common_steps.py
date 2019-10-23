#!/usr/bin/env python3
from time import sleep
from dogtail.rawinput import typeText, pressKey, keyCombo, absoluteMotion, click
from behave import step
from qecore import get_application
from qecore.get_node import GetNode, get_center


@step('{m_btn} click "{name}" "{role_name}"')
@step('{m_btn} click "{name}" "{role_name}" in "{root}"')
@step('{m_btn} click "{name}" "{role_name}" that is "{attr}"')
@step('{m_btn} click "{name}" "{role_name}" that is "{attr}" in "{root}"')
@step('{m_btn} click "{name}" "{role_name}" with description "{descr}"')
@step('{m_btn} click "{name}" "{role_name}" with description "{descr}" in "{root}"')
@step('{m_btn} click "{name}" "{role_name}" with description "{descr}" that is "{attr}"')
@step('{m_btn} click "{name}" "{role_name}" with description "{descr}" that is "{attr}" in "{root}"')
def mouse_click(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (data, node):
        node.click(data.m_btn)


@step('Mouse over "{name}" "{role_name}"')
@step('Mouse over "{name}" "{role_name}" in "{root}"')
@step('Mouse over "{name}" "{role_name}" that is "{attr}"')
@step('Mouse over "{name}" "{role_name}" that is "{attr}" in "{root}"')
@step('Mouse over "{name}" "{role_name}" with description "{descr}"')
@step('Mouse over "{name}" "{role_name}" with description "{descr}" in "{root}"')
@step('Mouse over "{name}" "{role_name}" with description "{descr}" that is "{attr}"')
@step('Mouse over "{name}" "{role_name}" with description "{descr}" that is "{attr}" in "{root}"')
def mouse_over(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        absoluteMotion(*(get_center(node)))


@step('Make an action "{action}" for "{name}" "{role_name}"')
@step('Make an action "{action}" for "{name}" "{role_name}" in "{root}"')
@step('Make an action "{action}" for "{name}" "{role_name}" that is "{attr}"')
@step('Make an action "{action}" for "{name}" "{role_name}" that is "{attr}" in "{root}"')
@step('Make an action "{action}" for "{name}" "{role_name}" with description "{descr}"')
@step('Make an action "{action}" for "{name}" "{role_name}" with description "{descr}" in "{root}"')
@step('Make an action "{action}" for "{name}" "{role_name}" with description "{descr}" that is "{attr}"')
@step('Make an action "{action}" for "{name}" "{role_name}" with description "{descr}" that is "{attr}" in "{root}"')
def make_action(context, action=None, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        node.doActionNamed(action)


@step('Item "{name}" "{role_name}" found')
@step('Item "{name}" "{role_name}" found in "{root}"')
@step('Item "{name}" "{role_name}" is "{attr}"')
@step('Item "{name}" "{role_name}" is "{attr}" in "{root}"')
@step('Item "{name}" "{role_name}" with description "{descr}" is "{attr}"')
@step('Item "{name}" "{role_name}" with description "{descr}" is "{attr}" in "{root}"')
def node_attribute(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        assert node is not None, "Node was not found, it should be!"


@step('Item "{name}" "{role_name}" was not found')
@step('Item "{name}" "{role_name}" was not found in "{root}"')
@step('Item "{name}" "{role_name}" is not "{attr}"')
@step('Item "{name}" "{role_name}" is not "{attr}" in "{root}"')
@step('Item "{name}" "{role_name}" with description "{descr}" is not "{attr}"')
@step('Item "{name}" "{role_name}" with description "{descr}" is not "{attr}" in "{root}"')
def node_not_attribute(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=False):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        assert node is None, "Node was found, it should not be!"


@step('Item "{name}" "{role_name}" has text "{text}"')
@step('Item "{name}" "{role_name}" has text "{text}" in "{root}"')
@step('Item "{name}" "{role_name}" with description "{descr}" has text "{text}"')
@step('Item "{name}" "{role_name}" with description "{descr}" has text "{text}" in "{root}"')
def node_with_text(context, name=None, role_name=None, descr=None, text=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        assert text in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Instead the node has text: {node.text}"
        ))


@step('Item "{name}" "{role_name}" does not have text "{text}"')
@step('Item "{name}" "{role_name}" does not have text "{text}" in "{root}"')
@step('Item "{name}" "{role_name}" with description "{descr}" does not have text "{text}"')
@step('Item "{name}" "{role_name}" with description "{descr}" does not have text "{text}" in "{root}"')
def node_without_text(context, name=None, role_name=None, descr=None, text=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        assert not text in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Node was found with text: {node.text}"
        ))


@step('Item "{name}" "{role_name}" does not have description "{descr}"')
@step('Item "{name}" "{role_name}" does not have description "{descr}" in "{root}"')
@step('Item "{name}" "{role_name}" does not have description "{descr}" that is "{attr}"')
@step('Item "{name}" "{role_name}" does not have description "{descr}" that is "{attr}" in "{root}"')
def node_without_description(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, None, m_btn, attr, root, retry, expect_positive) as (_, node):
        assert not descr in node.description, "".join((
            f"Found node should not have description: {descr}\n",
            f"Instead the node has description: {node.description}"
        ))


@step('Wait until "{name}" "{role_name}" is "{attr}"')
@step('Wait until "{name}" "{role_name}" is "{attr}" in "{root}"')
@step('Wait until "{name}" "{role_name}" with description "{descr}" is "{attr}"')
@step('Wait until "{name}" "{role_name}" with description "{descr}" is "{attr}" in "{root}"')
def wait_until_attr(context, name=None, role_name=None, descr=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    with GetNode(context, name, role_name, descr, m_btn, attr, root, retry, expect_positive) as (_, node):
        time_went_by = 0
        while not node.sensitive and time_went_by < 15:
            time_went_by += 0.5
            sleep(0.5)


#@step('Start another instance of "{application}" via "{start_via}"') # to be solved
#@step('Start another instance of "{application}" via command:"{command}"') # to be solved
@step('Start {application} via {start_via}') # behave-common-steps decorator
@step('Start "{application}" via command in {session}') # behave-common-steps decorator
@step('Start application "{application}" via "{start_via}"')
@step('Start application "{application}" via command "{command}"')
@step('Start application "{application}" via command in "{session}"')
@step('Start application "{application}" via command "{command}" in "{session}"')
def start_application(context, application=None, start_via="command", command=None, session=None):
    application = get_application(context, application)
    if start_via == "menu":
        try:
            application.start_via_menu()
        except Exception:
            application.start_via_menu()
    elif start_via == "command":
        try:
            application.start_via_command(command=command, in_session=session)
        except Exception:
            application.start_via_command(command=command, in_session=session)
    else:
        raise AssertionError("Only defined options are 'command' and 'menu'.")


@step('Close app via gnome panel') # behave-common-steps decorator
@step('Close application "{application}" via "{close_via}"')
def application_in_not_running(context, application=None, close_via="gnome panel"):
    application = get_application(context, application)
    if close_via == "gnome panel":
        context.execute_steps(f'* Left click "{application.name}" "menu" in "gnome-shell"')
        sleep(0.5)
        context.execute_steps('* Left click "Quit" "label" in "gnome-shell"')

    elif close_via == "application menu":
        application.instance.children[0][0].click(3)
        context.execute_steps(f'* Left click "Close" "label" in "gnome-shell"')

    elif close_via == "shortcut":
        application.close_via_shortcut()

    elif close_via == "kill command":
        application.kill_application()

    else:
        raise AssertionError("".join((
            "Only defined options are:\n",
            "'gnome panel', 'application menu', 'shortcut' and 'kill command'."
        )))


@step('{application} shouldn\'t be running anymore') # behave-common-steps decorator
@step('Application "{application}" is no longer running')
def application_is_not_running(context, application):
    application = get_application(context, application)
    if application.is_running():
        application.wait_before_app_closes(15)


@step('{application} should start') # behave-common-steps decorator
@step('Application "{application}" is running')
def application_is_running(context, application):
    application = get_application(context, application)
    application.already_running()
    if not application.is_running():
        application.wait_before_app_starts(15)


@step('Click "{target_name}" in GApplication menu') # behave-common-steps decorator
def click_gapp_menu(context, target_name):
    assert context.sandbox.default_application is not None, \
        "You need to define a default application if you are using steps without root."
    context.execute_steps(f'* Left click "{context.sandbox.default_application.name}" "menu" in "gnome-shell"')
    sleep(0.5)
    context.execute_steps(f'* Left click "{target_name}" "label" in "gnome-shell"')


@step('Type text: "{text}"')
def type_text(context, text):
    typeText(text)


@step('Press key: "{key_name}"')
def press_key(context, key_name):
    pressKey(key_name)


@step('Press "{combo_name}"') # behave-common-steps decorator
@step('Key combo: "{combo_name}"')
def key_combo(context, combo_name):
    keyCombo(combo_name)


@step('Wait {number} second before action')
@step('Wait {number} seconds before action')
def wait_up(context, number):
    sleep(int(number))


@step('Move mouse to: x: "{position_x}", y: "{position_y}"')
def absolutie_motion(context, position_x, position_y):
    absoluteMotion(int(position_x), int(position_y))


@step('{button} click on: x: "{position_x}", y: "{position_y}"')
def click_on_position(context, button, position_x, position_y):
    buttons = dict(Left=1, Middle=2, Right=3)
    click(int(position_x), int(position_y), buttons[button])
