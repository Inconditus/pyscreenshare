#!/usr/bin/env python
#based on https://github.com/engla/keybinder

#run:
#nohup python pyscreenshare.py &
#in the terminal, then close the terminal, for background use. 
#HOWEVER, remember to disable the raw_input for dropbox variables doen there V


#james' api dev keys
imgur_key = "033411dd9bf3e46d7057181f2c6dd9af"
pastebin_key = "8c004503e21ec60043fe7dabadf63a21"

#dropbox UID? dropbox basic save location?
#cheap way of finding home folder/dropbox folder
#db_username = raw_input("what's your linux username? (case sensative):")
#db_uid = raw_input("what's your dropbox id?:")
db_username = "james"
db_uid = "25486956"
db_saveloc = "/home/" + db_username +"/Dropbox/Public/Snapshots/"


#choose uploader
uploader = "imgur"
#"imgur","local","basic_dropbox","dropbox_api"(not done)

################################################################################
#Import needed libs
import os
import sys
import time
from urllib import urlopen, urlencode
import cStringIO
import StringIO
import base64
from xml.dom import minidom
#print tempfile.gettempdir() prints current temp dir
import tempfile
import gc

#sudo aptitude install python-imaging
import Image
#sudo aptitude install python-wxversion
#import wx
#sudo aptitude install python-gtk2
import gtk
import pygtk
pygtk.require('2.0')
#sudo aptitude install python-keybinder
import keybinder
#sudo aptitude install python-pycurl
import pycurl

#sudo aptitude install python-imaging python-wxversion python-gtk2 python-keybinder python-pycurl



#beep sound
def beep():
    print "\a"

#save and load gtk pixbuffs
def get_encoded_buffer_from_pixbuf(pixbuf): 
#"""Pixbuf To Encoded Buffer""" 
    io = StringIO.StringIO() 
    pixbuf.save_to_callback(io.write, "png") 
    encoded_buffer = base64.b64encode(io.getvalue()) 
    return encoded_buffer 
def get_pixbuf_from_encoded_buffer(buffer): 
#"""Encoded Buffer To Pixbuf""" 
    pixbuf_loader = gtk.gdk.pixbuf_loader_new_with_mime_type("image/png") 
    pixbuf_loader.write(base64.b64decode(buffer)) 
    pixbuf_loader.close() 
    pixbuf = pixbuf_loader.get_pixbuf() 
    return pixbuf
#pixbuf to image
def pixbuf2Image(pb):
    assert(pb.get_colorspace() == gtk.gdk.COLORSPACE_RGB)
    dimensions = pb.get_width(), pb.get_height()
    stride = pb.get_rowstride()
    pixels = pb.get_pixels()
    mode = pb.get_has_alpha() and "RGBA" or "RGB"
    return Image.frombuffer(mode, dimensions, pixels,
                            "raw", mode, stride, 1)

    
#paste to clipboard
def pasteclip(topaste):
    clipboard = gtk.clipboard_get()
    clipboard.set_text(topaste)
    clipboard.store()
#copy from clipboard
def copyclip():
    clipboard = gtk.clipboard_get()
    image = clipboard.wait_for_image()
    if image == None:
        text = clipboard.wait_for_text()
        clipboard.store()
        return (1, text)
    else:
        clipboard.store()
        return (0, image)
        
#upload code

#for imgur images
def up_imgur(imgdata):
    print "starting upload..."
    c = pycurl.Curl()
    response = cStringIO.StringIO()
    imageURL = ""
    error = ""

    values = [("key", imgur_key),
        #("image", (c.FORM_FILE, "file.png"))]
        #OR:("image", "http://example.com/example.jpg")]
        #OR:
        ("image", get_encoded_buffer_from_pixbuf(imgdata))]

    c.setopt(c.URL, "http://api.imgur.com/2/upload.xml")
    c.setopt(c.HTTPPOST, values)
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()
    try:
		# parse the XML return string and get the URL of our image
		xml = minidom.parseString(response.getvalue())
		imageURL = xml.getElementsByTagName("original")[0].firstChild.data
    except:
	    error = "Problem uploading anonymously."
    if error == "Problem uploading anonymously.":
        return error
    else: 
    	beep()
    	return imageURL 
    
#for local images
def up_local(imgdata):
    format = 'png'
    screenshot_name = 'Snapshot_' + time.strftime('%Y_%m_%d_%H_%M_%S')
    imgdata.save(screenshot_name + format, format)
    beep()
    return "locally saved"
    
#for local basic dropbox integration
def up_bdropbox(imgdata):
    format = 'png'
    screenshot_name = 'Snapshot_' + time.strftime('%Y_%m_%d_%H_%M_%S') + "."
    #db_saveloc = "/home/james/Dropbox/Public/Snapshots/"
    im = pixbuf2Image(imgdata)
    im.save(db_saveloc + screenshot_name + format, "PNG")#,quality=80
    #imgdata.save(screenshot_name + format, format)
    beep()
    return "http://dl.dropbox.com/u/" + db_uid + "/Snapshots/" + screenshot_name + format
    
    
#upload string to pastebin
def up_pastebin(stingdat):
    print "starting upload..."
    url="http://pastebin.com/api_public.php"
    args={"paste_code": stingdat, 
        "paste_private":1,
        "api_dev_key": pastebin_key,
        "paste_expire_date":"N",#10M", ###('N', '10M', '1H', '1D', '1M')
        "paste_format":"text"}
    full_url = urlopen(url,urlencode(args)).read()
    beep()
    return "http://pastebin.com/raw.php?i=" + full_url[20:]
    

#upload changer
def upload(imgdata):
    if uploader == "imgur":
        ret = up_imgur(imgdata)
    elif uploader == "local":
        ret = up_local(imgdata)
    elif uploader == "basic_dropbox":
        ret = up_bdropbox(imgdata)
    elif uploader == "dropbox_api":
        ret = False
        print "dropbox api upload not implemented yet"
    
    return ret








# Define user screencap functions!
def take_window(user_data):
    print "taking a shot of current window"
    # Calculate the size of the whole screen
    screenw = gtk.gdk.screen_width()
    screenh = gtk.gdk.screen_height()
    # Get the root and active window
    root = gtk.gdk.screen_get_default()
    if root.supports_net_wm_hint("_NET_ACTIVE_WINDOW") and root.supports_net_wm_hint("_NET_WM_WINDOW_TYPE"):
        active = root.get_active_window()
        # You definately do not want to take a screenshot of the whole desktop, see entry 23.36 for that
        # Returns something like ('ATOM', 32, ['_NET_WM_WINDOW_TYPE_DESKTOP'])
        if active.property_get("_NET_WM_WINDOW_TYPE")[-1][0] == '_NET_WM_WINDOW_TYPE_DESKTOP':
            print "return False error 1"
        # Calculate the size of the wm decorations
        relativex, relativey, winw, winh, d = active.get_geometry() 
        w = winw + (relativex*2)
        h = winh + (relativey+relativex)
        # Calculate the position of where the wm decorations start (not the window itself)
        screenposx, screenposy = active.get_root_origin()
    else: 
        print "return False error 2"
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, w, h),
        gtk.gdk.get_default_root_window(),
        gtk.gdk.colormap_get_system(),
        screenposx, screenposy, 0, 0, w, h)

    pic_url = upload(screenshot)
    pasted = pasteclip(pic_url)
    del screenshot
    gc.collect()
    print "done image window, pasted into clipboard:", pic_url
def take_screen(user_data):
    print "taking a shot of whole screen"
    # Either "png" or "jpeg"
    ##format = "jpeg"
    #grab from gtk
    width = gtk.gdk.screen_width()
    height = gtk.gdk.screen_height()
    screenshot = gtk.gdk.Pixbuf.get_from_drawable(
        gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height),
        gtk.gdk.get_default_root_window(),
        gtk.gdk.colormap_get_system(),
        0, 0, 0, 0, width, height)
    ##screenshot.save("image.jpg", format, {"quality": "70"})
    pic_url = upload(screenshot)
    pasted = pasteclip(pic_url)
    del screenshot
    gc.collect()
    print "done image screen, pasted into clipboard:", pic_url 
    ##print'ScreenShot_'+time.strftime('%Y_%m_%d%_%H_%M_%S')
def take_area(user_data):
    print "taking a shot of an area"
    print "taking a pic of just an area is not implemented yet"
def take_clipboard(user_data):
    print "upload clipboard"
    copyobj = copyclip()
    if copyobj[0] == 0:
        pic_url = upload(copyobj[1])
        pasted = pasteclip(pic_url)
        print "done clipboard image, pasted into clipboard:", pic_url 
    else: 
        textlink = up_pastebin(copyobj[1])
        pasted = pasteclip(textlink)
        print "done text clipboard, pasted link into clipboard:", textlink 
def take_file(user_data):
    print "upload file (to dropbox?)"
    print "uploading a file is not implemented yet"













# Define a function to exit the program
def exiter(user_data):
    print "exit with", user_data
    gtk.main_quit()

#binding hotkeys:
if __name__ == '__main__':
    #define hotkeys
    keystr_window = "<Shift><Ctrl>F2"
    keystr_screen = "<Shift><Ctrl>F3"
    keystr_area = "<Shift><Ctrl>F4"
    keystr_clipboard = "<Shift><Ctrl>F5"
    keystr_file = "<Shift><Ctrl>F6"
    keystr_exit = "<Alt><Ctrl>P"

    #define binds
    #all this crap is run through gtk.accelerator_parse
    keybinder.bind(keystr_window, take_screen, "Keystring %s (user data)" % keystr_window)
    keybinder.bind(keystr_screen, take_window, "Keystring %s (user data)" % keystr_screen)
    keybinder.bind(keystr_area, take_area, "Keystring %s (user data)" % keystr_area)
    keybinder.bind(keystr_clipboard, take_clipboard, "Keystring %s (user data)" % keystr_clipboard)
    keybinder.bind(keystr_file, take_file, "Keystring %s (user data)" % keystr_file)
    keybinder.bind(keystr_exit, exiter, "Keystring %s (user data)" % keystr_exit)
    
    #unbind stuff
    #keybinder.unbind(keystring)
    
    #do stuff
    print "Press", keystr_exit, "to quit"
    print keystr_window, "screencap"
    print keystr_screen, "windowcap (some bugs, notably google chrome)"
    print keystr_area, "areacap (not implemented)"
    print keystr_clipboard, "upload clipboard"
    print keystr_file, "upload file (not implemented)"
    #call gtk function
    gtk.main()
