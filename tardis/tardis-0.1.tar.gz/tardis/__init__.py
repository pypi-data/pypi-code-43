#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2019 Cédric Krier.
# Copyright (C) 2012 Antoine Smolders
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime as dt
import calendar
import gettext
import configparser
import os
import urllib.parse

import gi
import caldav
import dateutil.tz
import vobject
from dateutil.relativedelta import relativedelta

gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GooCanvas  # noqa: F401
import goocalendar  # noqa: F401

__all__ = ['Tardis']

_ = gettext.gettext
tzlocal = dateutil.tz.tzlocal()


class Calendar(goocalendar.Calendar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_has_tooltip(True)
        self.select(dt.date.today())
        self.connect('event-released', Calendar.on_event_released)

    def on_event_released(self, event):
        event.sync_event2dav()
        event.save()

    def edit_event(self, event, parent):
        dialog = EventDialog(parent, event=event)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dialog.save()
            self.update()
        dialog.destroy()

    def new_event(self, day, parent):
        event = Event('', day)
        dialog = EventDialog(parent, event)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            event = dialog.save()
            self.event_store.add(event)
            self.update()
        dialog.destroy()


class Event(goocalendar.Event):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dav_calendar = kwargs.get('dav_calendar')
        self.dav_event = kwargs.get('dav_event')
        if self.dav_event:
            self.sync_dav2event()

    def sync_dav2event(self):
        vevent = self.dav_event.instance.vevent
        dtstart = vevent.dtstart.value
        if not isinstance(dtstart, dt.datetime):
            dtstart = dt.datetime.combine(dtstart, dt.time(0))
            self.all_day = True
        else:
            self.all_day = False
        if getattr(dtstart, 'tzinfo', None):
            dtstart = dtstart.astimezone(tzlocal).replace(tzinfo=None)
        dtend = None
        if hasattr(vevent, 'dtend') and vevent.dtend.value:
            dtend = vevent.dtend.value
            if getattr(dtend, 'tzinfo', None):
                dtend = dtend.astimezone(tzlocal).replace(tzinfo=None)
            if not isinstance(dtend, dt.datetime):
                dtend = dt.datetime.combine(dtend, dt.time(0))
        # TODO duration
        self.start = dtstart
        self.end = dtend
        self.caption = vevent.summary.value

    def sync_event2dav(self):
        dav_event = self.dav_event
        vevent = dav_event.instance.vevent
        vevent.summary.value = self.caption
        if self.all_day:
            vevent.dtstart.value = self.start.date()
        else:
            vevent.dtstart.value = self.start.replace(tzinfo=tzlocal)
        if self.end:
            if self.all_day:
                vevent.dtend.value = self.end.date()
            else:
                vevent.dtend.value = self.end.replace(tzinfo=tzlocal)
        elif hasattr(vevent, 'dtend'):
            del vevent.dtend
        # TODO reset duration

    def save(self):
        self.dav_event.save()
        return self

    def load(self):
        self.dav_event.load()
        return self


class EventDialog(Gtk.MessageDialog):

    def __init__(self, parent, event):
        super().__init__(
            transient_for=parent, modal=True, destroy_with_parent=True,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=_('Tardis - Event'))
        self.set_default_response(Gtk.ResponseType.OK)
        self.event = event

        self.summary = Gtk.Entry()
        self.summary.set_text(event.caption)
        self.vbox.pack_start(
            self.summary, expand=False, fill=False, padding=0)

        self.date_start = DateEntry()
        self.date_start.set_date(event.start)
        self.time_start = TimeEntry()
        self.time_start.set_time(event.start)
        self.date_end = DateEntry()
        self.date_end.set_date(event.end or event.start)
        self.time_end = TimeEntry()
        self.time_end.set_time(event.end or event.start)
        dates = Gtk.HBox()
        for widget in (self.date_start, self.time_start,
                Gtk.Label(_('to')),
                self.date_end, self.time_end):
            dates.pack_start(
                widget, expand=False, fill=False, padding=0)
        self.vbox.pack_start(
            dates, expand=False, fill=False, padding=0)

        self.all_day = Gtk.CheckButton(_('All day'))
        self.all_day.connect('toggled', self.all_day_toggled)
        self.all_day.set_active(self.event.all_day)
        self.vbox.pack_start(
            self.all_day, expand=False, fill=False, padding=0)

        table = Gtk.Table(1, 2)
        self.vbox.pack_start(
            table, expand=False, fill=False, padding=0)

        table.attach(Gtk.Label(_('Calendar')), 0, 1, 0, 1)
        self.calendar = Gtk.ComboBoxText()
        for i, section in enumerate(parent.config.sections()):
            self.calendar.append_text(section)
            if section == event.dav_calendar:
                self.calendar.set_active(i)
        if self.calendar.get_active() == -1:
            self.calendar.set_active(0)
        table.attach(self.calendar, 1, 2, 0, 1)

        self.show_all()
        self.all_day_toggled(self.all_day)

    def all_day_toggled(self, all_day):
        if all_day.get_active():
            self.time_start.hide()
            self.time_end.hide()
        else:
            self.time_start.show()
            self.time_end.show()

    def get_dtstart(self):
        dtstart = self.date_start.get_date() or dt.date.today()
        if not self.all_day.get_active():
            time = self.time_start.get_time()
            if time:
                dtstart = dt.datetime.combine(dtstart, time)
                dtstart.replace(tzinfo=tzlocal)
        return dtstart

    def get_dtend(self):
        dtend = self.date_end.get_date()
        if dtend and not self.all_day.get_active():
            time = self.time_end.get_time()
            if time:
                dtend = dt.datetime.combine(dtend, time)
                dtend.replace(tzinfo=tzlocal)
        return dtend

    def save(self):
        section = self.calendar.get_active_text()
        parent = self.props.transient_for
        url = parent.config.get(section, 'url')
        color = 'blue'
        if parent.config.has_option(section, 'color'):
            color = parent.config.get(section, 'color')
        self.event.bg_color = color
        dav_client = caldav.DAVClient(url)
        dav_calendar = caldav.objects.Calendar(dav_client, url)
        if not self.event.dav_event:
            self.event.dav_event = caldav.objects.Event(dav_client,
                parent=dav_calendar)
            ical = vobject.iCalendar()
            ical.add('vevent')
            self.event.dav_event.instance = ical
        dav_event = self.event.dav_event
        url = urllib.parse.urlparse(url)
        if dav_event.parent.url != dav_calendar.url:
            dav_event.delete()
            dav_event.url = None
            dav_event.parent = dav_calendar

        def set_attribute(vevent, attr, value):
            if value is None:
                if hasattr(vevent, attr):
                    delattr(vevent, attr)
                return
            if not hasattr(vevent, attr):
                vevent.add(attr)
            getattr(vevent, attr).value = value

        vevent = dav_event.instance.vevent
        set_attribute(vevent, 'summary', self.summary.get_text())
        set_attribute(vevent, 'dtstart', self.get_dtstart())
        set_attribute(vevent, 'dtend', self.get_dtend())

        self.event.sync_dav2event()
        self.event.all_day = self.all_day.get_active()
        return self.event.save()


class DateEntry(Gtk.Entry):

    def set_date(self, date):
        if date:
            self.set_text(date.strftime('%x'))
        else:
            self.set_text('')

    def get_date(self):
        try:
            return dt.datetime.strptime(self.get_text(), '%x').date()
        except ValueError:
            return


class TimeEntry(Gtk.Entry):

    def set_time(self, time):
        if time:
            self.set_text(time.strftime('%X'))
        else:
            self.set_text('')

    def get_time(self):
        try:
            return dt.datetime.strptime(self.get_text(), '%X').time()
        except ValueError:
            return


class Toolbar(Gtk.Toolbar):

    def __init__(self, calendar):
        super().__init__()
        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.calendar = calendar
        self.accel_group = Gtk.AccelGroup()

        today_button = Gtk.ToolButton(label=_('Today'))
        today_button.set_tooltip_text(_('Today'))
        today_button.set_homogeneous(False)
        today_button.connect('clicked', lambda b:
            self.calendar.select(dt.date.today()))
        today_button.add_accelerator('clicked', self.accel_group,
            Gdk.KEY_T, Gdk.ModifierType.MODIFIER_MASK, Gtk.AccelFlags.VISIBLE)
        self.insert(today_button, -1)

        go_back = Gtk.ToolButton('gtk-go-back')
        go_back.set_expand(False)
        go_back.set_homogeneous(False)
        go_back.connect('clicked', lambda b: self.calendar.previous_page())
        self.insert(go_back, -1)

        self.current_page = Gtk.ToggleToolButton()
        self.current_page.connect('clicked', self.on_current_page_clicked)
        self.insert(self.current_page, -1)

        small_cal = Gtk.Calendar()
        small_cal.connect('day-selected', self.on_small_cal_day_selected)
        small_cal.set_display_options(
            Gtk.CalendarDisplayOptions.SHOW_HEADING |
            Gtk.CalendarDisplayOptions.SHOW_WEEK_NUMBERS |
            Gtk.CalendarDisplayOptions.SHOW_DAY_NAMES)
        small_cal.set_no_show_all(True)
        small_cal_item = GooCanvas.CanvasWidget(widget=small_cal)
        small_cal_item.set_property(
            'visibility', GooCanvas.CanvasItemVisibility.INVISIBLE)
        self.calendar.get_root_item().add_child(small_cal_item, -1)
        self.small_cal = small_cal
        self.small_cal_item = small_cal_item
        self.calendar.connect('day-selected',
            self.on_calendar_day_selected)

        go_forward = Gtk.ToolButton('gtk-go-forward')
        go_forward.set_expand(False)
        go_forward.set_homogeneous(False)
        go_forward.connect('clicked', lambda b: self.calendar.next_page())
        self.insert(go_forward, -1)

        previous_year = Gtk.ToolButton('gtk-go-back')
        previous_year.set_expand(False)
        previous_year.set_homogeneous(False)

        def on_previous_year(button):
            date = self.calendar.selected_date
            self.calendar.select(date + relativedelta(years=-1))
        previous_year.connect('clicked', on_previous_year)
        self.insert(previous_year, -1)

        self.current_year = Gtk.ToolButton()
        self.insert(self.current_year, -1)

        next_year = Gtk.ToolButton('gtk-go-forward')
        next_year.set_expand(False)
        next_year.set_homogeneous(False)

        def on_next_year(button):
            date = self.calendar.selected_date
            self.calendar.select(date + relativedelta(years=1))
        next_year.connect('clicked', on_next_year)
        self.insert(next_year, -1)

        blank_widget = Gtk.ToolItem()
        blank_widget.set_expand(True)
        self.insert(blank_widget, -1)

        week_button = Gtk.RadioToolButton()
        week_button.set_label(_('Week'))
        week_button.connect('clicked',
            lambda b: self.calendar.set_view('week'))
        week_button.add_accelerator('clicked', self.accel_group, Gdk.KEY_W,
            Gdk.ModifierType.MODIFIER_MASK, Gtk.AccelFlags.VISIBLE)
        self.insert(week_button, -1)

        month_button = Gtk.RadioToolButton.new_from_widget(week_button)
        month_button.set_label(_('Month'))
        month_button.connect('clicked',
            lambda b: self.calendar.set_view('month'))
        month_button.add_accelerator('clicked', self.accel_group,
            Gdk.KEY_M, Gdk.ModifierType.MODIFIER_MASK, Gtk.AccelFlags.VISIBLE)
        month_button.set_active(True)
        self.insert(month_button, -1)
        self.update_displayed_date()
        self.calendar.connect('page-changed',
            lambda *a: self.update_displayed_date())
        self.calendar.connect('view-changed',
            lambda *a: self.update_displayed_date())

    def on_current_page_clicked(self, button):
        small_cal_item = self.small_cal_item
        visibility = small_cal_item.get_property('visibility')
        if visibility == GooCanvas.CanvasItemVisibility.VISIBLE:
            small_cal_item.set_property(
                'visibility', GooCanvas.CanvasItemVisibility.INVISIBLE)
        else:
            small_cal_item.set_property(
                'visibility', GooCanvas.CanvasItemVisibility.VISIBLE)

    def on_small_cal_day_selected(self, calendar):
        year, month, day = calendar.get_date()
        self.calendar.select(dt.date(year, month + 1, day))

    def on_calendar_day_selected(self, calendar, date):
        self.small_cal.select_month(date.month - 1, date.year)
        self.small_cal.select_day(date.day)

    def update_displayed_date(self):
        date = self.calendar.selected_date
        self.current_year.set_label(str(date.year))
        if self.calendar.view == 'month':
            new_label = calendar.month_name[date.month]
            self.current_page.set_label(new_label)
        else:
            week_number = dt.date(date.year, date.month,
                date.day).isocalendar()[1]
            new_label = '%s %s' % (_('Week'), week_number)
            new_label += ' (' + calendar.month_name[date.month] + ')'
            self.current_page.set_label(new_label)


class Tardis(Gtk.Window):

    def __init__(self, config=None):
        super().__init__()
        self.set_title(_('Tardis'))
        self.set_icon(GdkPixbuf.Pixbuf.new_from_file(
                os.path.join(os.path.dirname(__file__),
                    'tardis.png').encode('utf-8')))
        self.connect('destroy', lambda w: Gtk.main_quit())

        self.event_store = goocalendar.EventStore()
        self.calendar = Calendar(self.event_store)
        if config is None:
            config = configparser.ConfigParser()
            config.read(['tardis.cfg', os.path.expanduser('~/.tardis.cfg')])
        self.config = config

        self.set_events()

        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.pack_start(
            Toolbar(self.calendar), expand=False, fill=False, padding=0)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add_with_viewport(self.calendar)
        scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(
            scrolled_window, expand=True, fill=True, padding=0)

        self.calendar.connect('page-changed', lambda *a: self.set_events())
        self.calendar.connect('event-activated', Calendar.edit_event, self)
        self.calendar.connect('day-activated', Calendar.new_event, self)

        self.show_all()

    def run(self):
        Gtk.main()

    def set_events(self):
        cal = calendar.Calendar(self.calendar.firstweekday)
        weeks = goocalendar.util.my_monthdatescalendar(cal,
            self.calendar.selected_date)
        first_date = dt.datetime.combine(weeks[0][0], dt.time.min)
        last_date = dt.datetime.combine(
            weeks[5][6] + dt.timedelta(1), dt.time.max)

        self.event_store.clear()
        for section in self.config.sections():
            url = self.config.get(section, 'url')
            color = 'blue'
            if self.config.has_option(section, 'color'):
                color = self.config.get(section, 'color')
            dav_client = caldav.DAVClient(url)
            dav_calendar = caldav.objects.Calendar(dav_client, url)
            events = dav_calendar.date_search(first_date, last_date)
            # TODO manage recurring events
            for event in events:
                gevent = Event('', dt.datetime.now(),
                    dav_calendar=section, dav_event=event, bg_color=color)
                self.event_store.add(gevent)


def main():
    Tardis().run()


if __name__ == '__main__':
    main()
