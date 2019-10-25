#
# Copyright (c) 2013, 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import string
from datetime import datetime, timedelta
from email.header import decode_header
from smtp_common import \
    get_streams_from_message, \
    get_properties_from_message, \
    get_body_text_from_message

"""
TODO: this creates a new task  . . . which is a valid option from things
like the workflow engine, however from a mail client it is not actually
possible - as the task does not exist to be a target.  This should be
"smtp_create_task" while send_to_task should take message body as a comment
and attach any attachments from the message!
"""
def smtp_send_to_task(
    from_, to_, message, context, service,
    mimetypes=['*', ],
    kind=None,
    executant_id=None,
    project_id=None,
    inbox=False,
    duration=7,
    priority=3,
    title_prefix='',
):
    # create task body
    subject = 'message had no subject'
    if message.has_key('subject'):
        subject = decode_header(message.get('subject'))[0]
        if subject[1] is not None:
            subject = subject[0].decode(subject[1]).encode('ascii', 'ignore')
        else:
            subject = subject[0]
    # create comment
    body_text = get_body_text_from_message(message)
    task_comment = 'FROM: {0}\nTO: {1}\nSUBJECT: {2}\n###\n{3}'.format(
        from_, to_, subject, body_text,
    ).encode('ascii', 'replace', )
    if len(task_comment) > 1024:
        task_comment = '{0}...'.format(task_comment[:1019])
    task = context.run_command(
        'task::new',
        values={
            'ownerobjectid': 8999,
            'executantobjectid': executant_id,
            'projectobjectid': project_id,
            'kind': kind,
            'title': '{0}{1}'.format(title_prefix, subject, ),
            'priority': priority,
            'startdate': datetime.today(),
            'enddate': datetime.today() + timedelta(days=duration),
            'comment': task_comment,
        },
    )
    for property_ in get_properties_from_message(message):
        value = ''.join(
            [x for x in str(property_[2]) if x in string.printable]
        )
        context.property_manager.set_property(
            task, property_[0], property_[1], value,
        )
    context.flush()  # noqa: if something is wrong, fail now, prior to attachment processing
    attachments = list()
    for mimetype in mimetypes:
        message_id, streams, rejects, = get_streams_from_message(
            message, '*', context.log, with_types=True,
        )
        for filename in streams.keys():
            if streams[filename][1].startswith('multipart/'):
                continue
            webdav_name = streams[filename][2]
            if webdav_name is None:
                webdav_name = filename
            if inbox:
                # TODO: love this way of storing, currently not really complete
                # as inbox'd documents
                context.run_command(
                    'document::inbox',
                    target=task,
                    filename=webdav_name,
                    mimetype=streams[filename][1],
                    stream=streams[filename][0],
                )
            else:
                # file as attachments
                attachments.append(
                    context.run_command(
                        'attachment::new',
                        entity=task,
                        mimetype=streams[filename][1],
                        kind=task.kind,
                        name=webdav_name,
                        handle=streams[filename][0],
                    )
                )
    if attachments:
        comment = ''
        for attachment in attachments:
            comment += (
                'Attachment {0} created from mail attachment of type "{1}"\n'
                .format(attachment.uuid, attachment.mimetype, )
            )
        context.run_command(
            'task::comment',
            task=task,
            values={'text': comment, }
        )

    return task
