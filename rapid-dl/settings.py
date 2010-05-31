# Settings frame for rapid-dl GUI

import wx
import cookielib
import urllib
import urllib2
import os

def load_cookie():
    if not os.path.exists(os.path.expanduser("~/.rapid-dl/cookies/gui.cookie")):
        dlg = wx.MessageDialog(None, "Cookies are not setup", "Warning", 
                               wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        return
    cj = cookielib.LWPCookieJar()
    cj.load(os.path.expanduser("~/.rapid-dl/cookies/gui.cookie"))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

def get_cookie(user, password):
    cookie_dir = os.path.expanduser("~/.rapid-dl/cookies")
    login_url = "https://ssl.rapidshare.com/cgi-bin/premiumzone.cgi"
    opts = {'login': user, 'password': password}
    data = urllib.urlencode(opts)
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    response = opener.open(login_url, data)
    if not os.path.exists(cookie_dir):
        os.makedirs(cookie_dir)
    cj.save(os.path.expanduser("~/.rapid-dl/cookies/gui.cookie"))

class Settings(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        cookie_settings = CookieSettings(self, -1)
        self.Centre()

class CookieSettings(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)

        self.parent = parent
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.txtFieldSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.username_txt = wx.TextCtrl(self, -1)
        self.password_txt = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD)

        self.txtFieldSizer.Add(self.username_txt, 0, wx.ALL, 10)
        self.txtFieldSizer.Add(self.password_txt, 0, wx.ALL, 10)

        close_btn = wx.Button(self, -1, label="Close")
        close_btn.Bind(wx.EVT_BUTTON, self.OnCloseBtn)
        get_btn = wx.Button(self, -1, label="Download cookies")
        get_btn.Bind(wx.EVT_BUTTON, self.OnGetBtn)

        self.btnSizer.Add(get_btn, 0, wx.ALL, 10)
        self.btnSizer.Add(close_btn, 0, wx.ALL, 10)

        self.mainSizer.Add(self.txtFieldSizer, 0)
        self.mainSizer.Add(self.btnSizer, 0)

        self.SetSizer(self.mainSizer)

    def OnCloseBtn(self, event):
        self.parent.Close()

    def OnGetBtn(self, event):
        print "Username =", self.username_txt.GetValue()
        print "Password =", self.password_txt.GetValue()
        get_cookie(self.username_txt.GetValue(), self.password_txt.GetValue())
        load_cookie()
        dlg = wx.MessageDialog(None, "Cookies are now loaded.", "Message",
                               wx.OK)
        dlg.ShowModal()
        self.parent.Close()
