from enum import Enum


class ActionName(Enum):
    WEB_ELEMENT_CLICK = "WebElementClick"
    WEB_ELEMENT_FIND_ELEMENT = "WebElementFindElement"
    WEB_ELEMENT_FIND_ELEMENTS = "WebElementFindElements"
    WEB_ELEMENT_SEND_KEYS = "WebElementSendKeys"
    WEB_ELEMENT_CLEAR = "WebElementClear"
    WEB_DRIVER_FIND_ELEMENT = "WebDriverFindElement"
    WEB_DRIVER_FIND_ELEMENTS = "WebDriverFindElements"
    WEB_DRIVER_GET = "WebDriverGet"
    WEB_DRIVER_QUIT = "WebDriverQuit"
    WEB_DRIVER_CLOSE = "WebDriverClose"
    WEB_DRIVER_NAVIGATE_TO = "WebDriverNavigateTo"
    WEB_DRIVER_MANAGE_LOGS_GET = "WebDriverManageLogsGet"
    WEB_DRIVER_MANAGE_LOG_ENTRIES_GET_ALL = "WebDriverManageLogEntriesGetAll"

    ACTION_MOVE_TO_ELEMENT = "MoveToElement"
    ACTION_CLICK_ELEMENT = "ClickOnElement"
    ACTION_CLICK = "Click"
    ACTION_KEY_DOWN = "KeyDown"
    ACTION_KEY_DOWN_ELEMENT = "WebElementKeyDown"
    ACTION_KEY_UP = "KeyUp"
    ACTION_WEB_ELEMENT_KEY_UP = "WebElementKeyUp"
    ACTION_SEND_KEYS = "SendKeys"
    ACTION_SEND_KEYS_ELEMENT = "WebElementSendKeys"
    ACTION_CLICK_AND_HOLD = "ClickAndHold"
    ACTION_WEB_ELEMENT_CLICK_AND_HOLD = "WebElementClickAndHold"
    ACTION_RELEASE = "Release"
    ACTION_WEB_ELEMENT_RELEASE = "ReleaseWebElement"

    ACTION_DOUBLE_CLICK = "DoubleClick"
    ACTION_WEB_ELEMENT_DOUBLE_CLICK = "WebElementDoubleClick"

    ACTION_MOVE_TO_ELEMENT_WITH_OFFSET = "Move To Element With Offset"

    ACTION_MOVE_BY_OFFSET = "MoveToElementByOffset"
    ACTION_WEB_ELEMENT_CONTEXT_CLICK = "WebElementContextClick"
    ACTION_CONTEXT_CLICK = "ContextClick"

    ACTION_DRAG_AND_DROP_ELEMENT_TO_ELEMENT = "DragAndDropElementToElement"
    ACTION_DRAG_AND_DROP_ELEMENT_BY_OFFSET = "DragAndDropElementByOffset"
    FAILED = "Failed"