#!/usr/bin/python

# rapidshare downloader

import wx
import os
import time

from downloader import DownloadList
from settings import Settings, load_cookie

class RapidGUIFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(800, 500))

        self.nb = wx.Notebook(self, -1)

        self.panel = wx.Panel(self.nb, -1)
        self.dl_list = DownloadList(self.nb)

        self.timer = wx.Timer(self.panel, 1)
        wx.EVT_TIMER(self.panel, 1, self.updateList)
        self.timer.Start(100)

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        # URLs textfield
        enterurls = wx.StaticText(self.panel, -1, "Enter URLs:")
        self.urls_txt = wx.TextCtrl(self.panel, -1, style=wx.TE_MULTILINE)

        # Download button
        download_btn = wx.Button(self.panel, -1, label='Download')
        download_btn.Bind(wx.EVT_BUTTON, self.OnDownloadBtn)

        # Clear button
        clear_btn = wx.Button(self.panel, -1, label='Clear')
        clear_btn.Bind(wx.EVT_BUTTON, self.OnClearBtn)

        # Settings button
        settings_btn = wx.Button(self.panel, -1, label='Settings')
        settings_btn.Bind(wx.EVT_BUTTON, self.OnSettingsBtn)

        self.buttonSizer.Add(download_btn, 0)
        self.buttonSizer.Add(clear_btn, 0, wx.LEFT | wx.ALIGN_RIGHT, 20)
        self.buttonSizer.Add(settings_btn, 0)

        # Add everything to the sizer
        self.vbox.Add(enterurls, 0, wx.LEFT, 10)
        self.vbox.Add(self.urls_txt, 2, wx.ALL | wx.EXPAND, 10)
        self.vbox.Add(self.buttonSizer, 0, wx.BOTTOM | wx.ALIGN_CENTER, 5)

        self.nb.AddPage(self.panel, 'URLs')
        self.nb.AddPage(self.dl_list, 'Current downloads')
        self.panel.SetFocus()
        self.panel.SetSizerAndFit(self.vbox)
        self.Centre()
        self.Show(True)

    def OnSettingsBtn(self, event):
        settingsframe = Settings(None, -1, "Settings")
        settingsframe.Show(True)

    def OnDownloadBtn(self, event):
        dial = wx.DirDialog(None, "Choose a download directory", 
                            style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dial.ShowModal() == wx.ID_OK:
            self.dl_path = dial.GetPath()
            passed = True
            for url in self.urls_txt.GetValue().splitlines():
                if not passed:
                    dlg = wx.MessageDialog(None, "Continue?", 
                                           'Error', wx.YES_NO)
                    cont = dlg.ShowModal() == wx.ID_YES
                    if not cont:
                        break
                self.dl_list.AddDownload(url, self.dl_path)
        dial.Destroy()

    def OnClearBtn(self, event):
        self.urls_txt.Clear()

    def updateList(self, event):
        self.dl_list.Update(event)
        self.nb.SetPageText(1, "Current downloads (%d)" % 
                            len(self.dl_list.GetDownloadPanels()))

class RapidGUI(wx.App):
    def OnInit(self):
        frame = RapidGUIFrame(None, -1, "Rapidshare Downloader")
        frame.Show(True)
        load_cookie()
        self.SetTopWindow(frame)
        return True

if __name__ == "__main__":
    app = RapidGUI(0)
    app.MainLoop()
