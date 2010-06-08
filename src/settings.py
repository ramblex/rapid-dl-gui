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

class Settings(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        
        self.nb = wx.Notebook(self, -1)

        cookie_settings = CookieSettings(self.nb, -1, self)

        self.nb.AddPage(cookie_settings, 'Cookies')
        self.Centre()

class CookieSettings(wx.Panel):
    def __init__(self, parent, id, frame):
        wx.Panel.__init__(self, parent, id)

        self.frame = frame
        self.parent = parent
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        # Panel 1
        panel1 = wx.Panel(self, -1)
        self.gridSizer = wx.GridSizer(2,2,10,10)
        self.gridSizer.Add(wx.StaticText(panel1, -1, 'Username:', (5,5)), 
                           0, wx.ALIGN_CENTER_VERTICAL)
        self.username_txt = wx.TextCtrl(panel1, -1, size=(150, -1)) 
        self.gridSizer.Add(self.username_txt)
        self.gridSizer.Add(wx.StaticText(panel1, -1, 'Password:', (5,5)),
                           0, wx.ALIGN_CENTER_VERTICAL)
        self.password_txt = wx.TextCtrl(panel1, -1, style=wx.TE_PASSWORD,
                                       size=(150, -1)) 
        self.gridSizer.Add(self.password_txt)
        panel1.SetSizer(self.gridSizer)

        # Panel 2
        panel2 = wx.Panel(self, -1)
        self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        close_btn = wx.Button(panel2, -1, label="Close")
        close_btn.Bind(wx.EVT_BUTTON, self.OnCloseBtn)
        get_btn = wx.Button(panel2, -1, label="Download cookies")
        get_btn.Bind(wx.EVT_BUTTON, self.OnGetBtn)
        self.btnSizer.Add(get_btn, 0, wx.ALL, 10)
        self.btnSizer.Add(close_btn, 0, wx.ALL, 10)
        panel2.SetSizer(self.btnSizer)

        self.mainSizer.Add(panel1, 0, 
                           wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.mainSizer.Add(panel2, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.SetSizer(self.mainSizer)
 
    def OnCloseBtn(self, event):
        self.frame.Close()

    def OnGetBtn(self, event):
        #print "Username =", self.username_txt.GetValue()
        #print "Password =", self.password_txt.GetValue()
        get_cookie(self.username_txt.GetValue(), self.password_txt.GetValue())
        load_cookie()
        dlg = wx.MessageDialog(None, "Cookies are now loaded.", "Message",
                               wx.OK)
        dlg.ShowModal()
        self.parent.Close()
