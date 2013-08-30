#!/usr/bin/python


import wx
import re

from storm import ssh_config
from storm.exceptions import StormValueError
from storm.ssh_uri_parser import parse
from getpass import getuser


class StormFrame(wx.Frame):

    ID_NEW, ID_EDIT, ID_REFRESH, ID_DELETE = 1, 2, 3, 4

    def __init__(self, parent, frame_id, title):

        wx.Frame.__init__(self, parent, frame_id, title, size=(660, 300))

        self.init_ui()

    def init_ui(self):
        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        about = fileMenu.Append(wx.ID_ABOUT, "&About","Information about this program")
        fileMenu.AppendSeparator()
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_quit, fitem)
        self.Bind(wx.EVT_MENU, self.on_about, about)

        self.listbox = wx.ListBox(panel, -1)
        hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)

        btnPanel = wx.Panel(panel, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.new = wx.Button(btnPanel, StormFrame.ID_NEW, 'New', size=(90, 30))
        self.edit = wx.Button(btnPanel, StormFrame.ID_EDIT, 'Edit', size=(90, 30))
        self.delete = wx.Button(btnPanel, StormFrame.ID_DELETE, 'Delete', size=(90, 30))
        self.reload = wx.Button(btnPanel, StormFrame.ID_REFRESH, 'Reload', size=(90, 30))

        self.edit.Enable(False)
        self.delete.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.create, id=StormFrame.ID_NEW)
        self.Bind(wx.EVT_BUTTON, self.on_edit, id=StormFrame.ID_EDIT)
        self.Bind(wx.EVT_BUTTON, self.on_delete, id=StormFrame.ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, id=StormFrame.ID_REFRESH)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_edit)
        self.Bind(wx.EVT_LISTBOX, self.activate_buttons)

        vbox.Add((-1, 20))
        vbox.Add(self.new)
        vbox.Add(self.edit, 0, wx.TOP, 5)
        vbox.Add(self.delete, 0, wx.TOP, 5)
        vbox.Add(self.reload, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        for ssh_connection in self.get_connection_list():
            self.listbox.Append(ssh_connection)

        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('Ready.')

        self.Centre()
        self.Show(True)

    def activate_buttons(self, event):
        self.toggle_buttons(True)

    def toggle_buttons(self, status):
        self.edit.Enable(status)
        self.delete.Enable(status)

    def get_connection_list(self):
        ssh_connection_list = []
        ssh_conf = ssh_config.ConfigParser()
        loaded_config = ssh_conf.load()
        for host_entry in loaded_config:

            if not host_entry.get("type") == 'entry' or host_entry.get("host") == '*':
                continue

            identifier = "[{host}] {user}@{hostname}".format(
                user=host_entry.get("options", {}).get("user", getuser()),
                hostname=host_entry.get("options", {}).get("hostname"),
                host=host_entry.get("host"),
            )

            ssh_connection_list.append(identifier)

        return ssh_connection_list

    def create(self, event):
        hostname = wx.GetTextFromUser('Enter a  name', 'Add connection')

        if hostname != '':
            connection_string = wx.GetTextFromUser('Connection string', 'Add connection')
            if connection_string != '':
                sconfig = ssh_config.ConfigParser()
                sconfig.load()

                options = self.parse_connection_uri(connection_string)
                sconfig.add_host(hostname, options)
                sconfig.write_to_ssh_config()
                self.listbox.Append("[%s] %s" % (hostname, connection_string))
                self.sb.SetStatusText('%s added to SSHConfig.' % hostname)

        self.toggle_buttons(False)

    def parse_connection_uri(self, connection_uri):
        options = dict()
        options["user"], options["hostname"], options["port"] = parse(connection_uri)
        return options

    def on_edit(self, event):

        selection = self.listbox.GetSelection()

        text = self.listbox.GetString(selection)
        result = re.search("^\[(.*)\] (.*)", text)
        if result:
            renamed = wx.GetTextFromUser('Edit item', 'Edit connection', result.group(2))

            if renamed != '':
                self.listbox.Delete(selection)
                new_entry = "[%s] %s " % (result.group(1), renamed)

                sconfig = ssh_config.ConfigParser()
                sconfig.load()

                options = self.parse_connection_uri(renamed)
                sconfig.update_host(result.group(1), options)
                sconfig.write_to_ssh_config()

                self.listbox.Insert(new_entry, selection)
                self.sb.SetStatusText('%s updated successfully.' % result.group(1))

        self.toggle_buttons(False)


    def show_message(self, message, message_type):
        icon_types = {
            'error': wx.ICON_ERROR,
            'info': wx.ICON_INFORMATION,
        }
        wx.MessageBox(message, message_type, wx.OK | icon_types.get(message_type))

    def on_delete(self, event):
        selection = self.listbox.GetSelection()

        sconfig = ssh_config.ConfigParser()
        sconfig.load()

        host_name = self.find_hostname(self.listbox.GetString(selection))

        try:
            sconfig.delete_host(host_name)
            sconfig.write_to_ssh_config()
            if selection != -1:
                self.listbox.Delete(selection)
                self.sb.SetStatusText('%s deleted successfully.' % host_name)

        except StormValueError as error:
            self.show_message(str(error), 'error')

        self.toggle_buttons(False)

    def find_hostname(self, connection_string):
        hostname = re.findall('^\[(.*)\]', connection_string)

        if len(hostname) > 0:
            return hostname[0]

    def on_refresh(self, event):
        self.listbox.Clear()
        self.listbox.Update()

        for ssh_connection in self.get_connection_list():
            self.listbox.Append(ssh_connection)

        self.sb.SetStatusText('SSHconfig reloaded.')
        self.toggle_buttons(False)

    def on_quit(self, text):
        self.Close()

    def on_about(self, text):
        self.show_message("stormssh-gui is a helper for connecting to your servers easily."
                          "\n\nbug reports: https://github.com/emre/storm-gui/issues", 'info')


def main():
    app = wx.App()
    StormFrame(None, -1, 'stormssh-gui')
    app.MainLoop()

if __name__ == '__main__':
    main()