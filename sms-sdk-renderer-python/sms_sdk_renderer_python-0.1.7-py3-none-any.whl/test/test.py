import sys
sys.path.insert(0, "/Users/reed.feldman/Desktop/SDK/render/sms-sdk-renderer-python/sms_sdk_renderer_python/lib")

import sms_sdk_renderer as SmsRenderer

simple_data = {
        "title":"test",
        "content":"testcontent"
}
# print(renderInBot(simple_data, smsTypes['SIMPLE']))

alert_data = {
    "title": 'Alert Title',
    "content": 'This is a danger alert'
}
# print(renderInBot(alert_data, smsTypes['ALERT']))

info_data = {
      "title": 'Informaiton Title',
      "content": 'This is a information message',
      "description": 'Information message description'
}

# print(renderInBot(info_data, smsTypes['INFORMATION']))

notification_data = {
  "title": 'My Title',

  #OPTIONAL - used to render alert syle notification
  "alert": True,

  #Content can be a smiple text
  "content": 'My content',
  #or an object that is rendered in </card>
  # content: {
  #   header: 'Content header',
  #   body: 'Content body'
  # },

  "description": 'My description',
  "comment": {
    "body": 'My comments'
  },
  "assignee": {
    "displayName": 'John Smith'
  },
  "showStatusBar": True,
  "type": {
    "name": 'message type'
  },
  "priority": {
    "name": 'message priority'
  },
  "status": {
    "name": 'message status'
  },
  "labels": [
    {
      "text": 'label1'
    },
    {
      "text": 'label2'
    }
  ]
}
# print(renderInBot(notification_data, smsTypes['NOTIFICATION']))

button_data = {
    "name": "example-button",
    "type": "action",
    "text": "Submit"
}

# print(renderInBot(button_data, smsTypes['BUTTON']))

checkbox_data = {
    "name":"example-name",
    "value":"example-value",
    "checked": "false",
    "text":"Red"
}

# print(renderInBot(checkbox_data, smsTypes['CHECKBOX']))

textfield_data = {
    "name":"exmaple-text-field",
    "placeholder": "example-placeholder",
    "required": "true",
    "masked": "true",
    "minlength": 1,
    "maxlength": 128
}

# print(renderInBot(textfield_data, smsTypes['TEXTFIELD']))

textarea_data = {
    "name":"exmaple-text-area",
    "placeholder": "example-placeholder",
    "required": "true"
}

# print(renderInBot(textarea_data, smsTypes['TEXTAREA']))

radiobutton_data = {
    "name":"example-name",
    "value":"example-value",
    "checked": "false",
    "text":"Red"
}

# print(renderInBot(radiobutton_data, smsTypes['RADIOBUTTON']))

personselector_data = {
    "name":"person-selector-name",
    "placeholder":"example-placeholder",
    "required":"true"
}

# print(renderInBot(personselector_data, smsTypes['PERSONSELECTOR']))

dropdownmenu_data = {
"name":"dropdown-name",
"required": "true",
"options": [{"value":"value1", "selected":"true", "text":"First Option"},
            {"value":"value2", "selected":"false", "text":"Second Option"},
            {"value":"value3", "selected":"true", "text":"Third Option"} ]

}

# print(renderInBot(dropdownmenu_data, smsTypes['DROPDOWN_MENU']))

table_data = {
        "select":{
            "position":"right",
            "type":"checkbox"
        },
        "header_list": ["H1", "H2", "H3"],
        "body": [["A1", "B1", "C1"],
                 ["A2", "B2", "C2"],
                 ["A3", "B3", "C3"]],
        "footer_list": ["F1", "F2", "F3"]
        }

print(SmsRenderer.renderInBot(table_data, SmsRenderer.smsTypes['TABLE_SELECT']))
