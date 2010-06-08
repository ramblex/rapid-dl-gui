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

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

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
            if not server_url.startswith("http://"):
                raise ValueError
            actual_url = self.get_actual_url(server_url)
            if not actual_url.startswith("http://"):
                raise ValueError
            request = urllib2.Request(actual_url)
            self.handle = urllib2.urlopen(request)
            if self.handle == None:
                raise ValueError
            return self.get_data(self.handle)
        except ValueError:
            self.parent.Remove(self.idx)
            dlg = wx.MessageDialog(None, "Invalid URL", "Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

    def get_server_url(self, url):
        """Find the server URL from a given rapidshare URL

        Arguments:
        - url: The URL which is shared 
               e.g. http://rapidshare.com/files/12038012/myfile.rar
        """
        request = urllib2.Request(url)
        handle = urllib2.urlopen(request)
        page = handle.read()
        idx = page.find("action=")
        if idx != -1:
            eol = page.find("\n", idx)
            return page[idx:eol].rsplit('"')[1]
        else:
            return ""

    def get_actual_url(self, server_url):
        """Find the download URL from a given server URL.
        
        Arguments:
        - server_url: A rapidshare server URL
                      e.g. http://rs1029.rapidshare.com/files/109238/myfile.rar
        """
        opts = {'dl.start': 'PREMIUM'}
        data = urllib.urlencode(opts)
        request = urllib2.Request(server_url, data)
        handle = urllib2.urlopen(request)
        page = handle.read()
        idx = page.find('name="dlf" action=')
        if idx != -1:
            eol = page.find("\n", idx)
            return page[idx:eol].rsplit('"')[3]
        return ""

    def filename(self):
        return self.handle.info().getheader('Content-disposition').split("=")[-1]

    def get_data(self, handle):
        """Download the data from the given handle and update the
        associated panel. Note that this will only update the data in
        the panel using its mutators and not the panel GUI since this
        method is probably being executed in a thread and hence should
        not update the GUI directly.
        """
        total_size = int(handle.info().getheader('Content-Length').strip())
        filename = handle.info().getheader('Content-disposition').split("=")[-1]
        one_percent = total_size / 1000.0
        bytes_so_far = 0.0
        out = open(self.dl_path+"/"+filename, "w")
        num_blocks = 0
        while 1:
            if num_blocks == 1:
                start_time = time.time()
                start_size = bytes_so_far
            chunk = handle.read(self.chunk_size)
            out.write(chunk)
            bytes_so_far += len(chunk)
            if not chunk or self.panel.cancelled:
                break
            percent_done = round((bytes_so_far / total_size) * 100, 2)
            self.panel.percent_done = percent_done
            if num_blocks == 50:
                elapsed = time.time() - start_time
                byte_rate = (bytes_so_far - start_size)
                bytes_left = total_size - bytes_so_far
                self.panel.eta = bytes_left / byte_rate
                self.panel.rate = byte_rate / elapsed / 1024
                num_blocks = 0
            num_blocks = num_blocks + 1
        return True

class DownloadListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    rows = []

    def __init__(self, parent, width):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        
        self.InsertColumn(0, 'Filename', width=400)
        self.InsertColumn(1, 'Percentage done', width=100)
        self.InsertColumn(2, 'Rate', width=100)
        self.InsertColumn(3, 'ETA', width=80)

    def AddDownload(self, url, dl_path):
        num_items = self.GetItemCount()
        self.InsertStringItem(num_items, url)
        p = DownloadPanel(self, num_items)
        self.rows.insert(num_items, p)
        downloader = Downloader(url, dl_path, p)
        thread = threading.Thread(target=downloader.download)
        thread.start()

    def Update(self, event):
        for row in self.rows:
            row.update()

    def num_dls(self):
        return self.GetItemCount()

class DownloadPanel():
    eta = 0
    rate = 0
    percent_done = 0
    cancelled = False

    def __init__(self, parent, idx):
        self.parent = parent
        self.idx = idx

    def update(self):
        self.parent.SetStringItem(self.idx, 1, "%d%%" % self.percent_done)
        self.parent.SetStringItem(self.idx, 2, "%d kB/s" % self.rate)
        self.parent.SetStringItem(self.idx, 3, 
                                  time.strftime("%H:%M:%S", time.gmtime(self.eta)))
