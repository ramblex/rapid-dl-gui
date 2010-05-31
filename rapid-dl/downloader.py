import cookielib
import commands
import urllib
import urllib2
import wx.lib.scrolledpanel as ScrolledPanel
import wx
import thread
import os
import threading
import time

def setup_cookie():
    cj = cookielib.LWPCookieJar()
    cj.load("/Users/alexduller/.rapid-dl/cookies/gui.cookie")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

class Downloader():
    chunk_size = 8192

    def __init__(self, url, dl_path, panel):
        # Setup downloader stuff
        self.url = url
        self.dl_path = dl_path
        self.panel = panel
    
    def download(self):
        """Get the real download URL for a given rapidshare
        URL. Return a handle to the URL"""
        try:
            server_url = self.get_server_url(self.url)
            if server_url == None:
                return None
            actual_url = self.get_actual_url(server_url)
            if actual_url == None:
                return None
            request = urllib2.Request(actual_url)
            self.handle = urllib2.urlopen(request)
            if self.handle != None:
                self.get_data()
            return True
        except ValueError:
            self.panel.Remove()
            dlg = wx.MessageDialog(None, "Invalid URL", "Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

    def get_server_url(self, url):
        """Find the server URL from a given rapidshare URL"""
        request = urllib2.Request(url)
        handle = urllib2.urlopen(request)
        page = handle.read()
        idx = page.find("action=")
        if idx != -1:
            eol = page.find("\n", idx)
            return page[idx:eol].rsplit('"')[1]
        else:
            return None

    def get_actual_url(self, server_url):
        """Find the download URL from a given server URL"""
        opts = {'dl.start': 'PREMIUM'}
        data = urllib.urlencode(opts)
        request = urllib2.Request(server_url, data)
        handle = urllib2.urlopen(request)
        page = handle.read()
        idx = page.find('name="dlf" action=')
        if idx != -1:
            eol = page.find("\n", idx)
            return page[idx:eol].rsplit('"')[3]
        return None

    def filename(self):
        return self.handle.info().getheader('Content-disposition').split("=")[-1]

    def get_data(self):
        total_size = int(self.handle.info().getheader('Content-Length').strip())
        one_percent = total_size / 1000.0
        bytes_so_far = 0.0
        out = open(self.dl_path+"/"+self.filename(), "w")
        num_blocks = 0
        while 1:
            if num_blocks == 1:
                start_time = time.time()
                start_size = bytes_so_far
            chunk = self.handle.read(self.chunk_size)
            out.write(chunk)
            bytes_so_far += len(chunk)
            if not chunk or self.panel.IsCancelled():
                break
            percent_done = round((bytes_so_far / total_size) * 100, 2)
            self.panel.SetPercentDone(percent_done)
            if num_blocks == 50:
                elapsed = time.time() - start_time
                byte_rate = (bytes_so_far - start_size)
                bytes_left = total_size - bytes_so_far
                self.panel.SetETA(bytes_left / byte_rate)
                self.panel.SetRate(byte_rate / elapsed / 1024)
                num_blocks = 0
            num_blocks = num_blocks + 1

class DownloadPanel(wx.Panel):
    cancelled = False
    rate = 0
    percent_done = 0
    remove = False
    eta = 0

    def __init__(self, parent, filename):
        wx.Panel.__init__(self, parent)
        menu_titles = ["Cancel"]
        self.filename = filename
        self.menu_title_by_id = {}
        for title in menu_titles:
            self.menu_title_by_id[wx.NewId()] = title

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.txt = wx.StaticText(self, -1, filename, style=wx.ALIGN_LEFT, 
                                 size=(400,25))
        self.txt.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.gauge = wx.Gauge(self, -1, 100, size=(90,25))
        self.complete_lbl = wx.StaticText(self, -1, "0%", size=(75,25))
        self.rate_lbl = wx.StaticText(self, -1, "Unknown", size=(100,25))
        self.eta_lbl = wx.StaticText(self, -1, "ETA: Unknown", size=(125,25))
        hbox.Add(self.txt, 0)
        hbox.Add(self.gauge, 0, wx.RIGHT, 10)
        hbox.Add(self.complete_lbl, 0)
        hbox.Add(self.rate_lbl, 0)
        hbox.Add(self.eta_lbl, 0)
        self.SetSizer(hbox)

    def Update(self):
        self.gauge.SetValue(self.percent_done)
        self.complete_lbl.SetLabel("%s%%" % self.percent_done)
        if self.IsCancelled():
            self.rate_lbl.SetLabel("(Cancelled)")
            self.eta_lbl.SetLabel("")
        elif self.IsCompleted():
            self.rate_lbl.SetLabel("(Completed)")
            self.eta_lbl.SetLabel("")
        else:
            self.rate_lbl.SetLabel("%d kB/s" % self.rate)
            e = time.strftime("%H:%M:%S", time.gmtime(self.eta))
            self.eta_lbl.SetLabel("ETA: "+e)

    def Remove(self):
        self.remove = True

    def ToBeRemoved(self):
        return self.remove

    def SetETA(self, eta):
        self.eta = eta

    def SetRate(self, r):
        self.rate = r

    def SetPercentDone(self, p):
        self.percent_done = p

    def IsCompleted(self):
        return (self.percent_done == 100)

    def IsCancelled(self):
        return self.cancelled

    def Cancel(self):
        self.cancelled = True

    def OnRightClick(self, event):
        menu = wx.Menu()
        for id, title in self.menu_title_by_id.items():
            menu.Append(id, title)
            wx.EVT_MENU(menu, id, self.MenuSelectionCb)
        self.PopupMenu(menu)
        menu.Destroy()

    def MenuSelectionCb(self, event):
        operation = self.menu_title_by_id[event.GetId()]
        if operation == "Cancel":
            dial = wx.MessageDialog(None, 'Are you sure you want to stop downloading %s' % self.filename, 'Cancel?', wx.YES_NO | wx.ICON_QUESTION)
            result = dial.ShowModal()
            if result == wx.ID_YES:
                self.Cancel()

class DownloadList(wx.lib.scrolledpanel.ScrolledPanel):
    dl_path = ""
    download_panels = []

    def __init__(self, parent):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        setup_cookie()
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)
        self.SetupScrolling()

    def AddDownload(self, url, dl_path):
        panel = DownloadPanel(self, os.path.basename(url))
        downloader = Downloader(url, dl_path, panel)
        thread = threading.Thread(target=downloader.download)
        thread.start()
        self.download_panels.append(panel)
        self.vbox.Add(panel)
        self.Layout()

    def Update(self, event):
        panels = self.download_panels[:]
        for panel in panels:
            if panel.ToBeRemoved():
                print "Removing panel"
                self.download_panels.remove(panel)
                self.vbox.Remove(panel)
            else:
                panel.Update()

    def GetDownloadPanels(self):
        return self.download_panels
