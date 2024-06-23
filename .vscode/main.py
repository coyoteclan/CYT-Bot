#||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Module Imports                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.metrics import dp
from re import split as splitstr
from re import sub
import socket
import sys
import threading
from os import path
from random import uniform as randomFloatRange
import json
from functools import partial
from time import sleep
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Config File Path                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

currentdir = path.dirname(path.realpath(__file__))
config_path = path.join(currentdir, "saved_servers.json")
#config_path = "/storage/emulated/0/Download/s.json"

if not path.isfile(config_path):
    open(config_path, 'w').close()

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Global Variables                    #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

global server_ip
global server_port
global rcon_password
server_ip = "1.1.1.1"
server_port = 28960
rcon_password = "12345"

myFont = path.join(currentdir, "font/playwritedegrund.ttf")
dejavu = path.join(currentdir, "font/dejavusans.ttf")

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    RCON Command Function                      #
#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

def rcon_command(server_ip="1.1.1.1", server_port=0, rcon_password="12345", command="status"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)

    rcon_query = f"\xff\xff\xff\xffrcon {rcon_password} {command}".encode('latin1')

    server_address = (server_ip, server_port)
    try:
        sock.sendto(rcon_query, server_address)
        response, _ = sock.recvfrom(4096)
        s = response.decode('latin1')
        return splitstr("print", s)[1].strip()

    except socket.timeout:
        return "Failed to connect to server: Request timed out"
    except Exception as e:
        return f"Failed to connect to server: {e}"
    finally:
        sock.close()

def monotone(name):
	name = sub(r'\^\^([0-7]{2})|\^([0-7]{1})|\^', '', name)
	return name

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Load Config Function                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

def loadSavedServers():
    with open(config_path, 'r') as f:
        try:
            savedServers = json.load(f)
            return savedServers
        except json.decoder.JSONDecodeError:
            str = "failed"
            return str
# Thanks to https://stackoverflow.com/a/54491411
# The program would crash if file is empty
# Program warr jana tha
#--------------------------------------------|
savedServers = loadSavedServers()#           |
#--------------------------------------------|

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Save Config Function                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

def saveServers(dict):
    with open(config_path, 'w') as f:
        json.dump(dict, f, indent=4)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    Re-write Config File                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#

def rewriteServers(dict):
    open(config_path, 'w').close()
    saveServers(dict)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
#                    App Construction                      #
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
Window.clearcolor = (0.2, 0.2, 0.2, 1)

class CoYoTeApp(App):
    def build(self):
        self.title = "CoYoTe' RCON*"
        self.icon = "./coyote_tool.ico"
        Window.top = True
        console_layout = BoxLayout(orientation='vertical', size_hint=(1, 1), pos=(0, 0), spacing=2)
        
        # Create and bind a button to open the popup
        topBar = AnchorLayout(size_hint=(1,0.05))
        button_layout = BoxLayout(orientation='horizontal')
        servers_button = Button(text='Servers', font_name="myfont", font_size=20)
        servers_button.bind(on_press=self.show_servers)
        maplist_btn = Button(text='Maps', font_name="myfont", font_size=20)
        maplist_btn.bind(on_press=self.show_maplist)
        self.maps = ""
        button_layout.add_widget(servers_button)
        button_layout.add_widget(maplist_btn)
        topBar.add_widget(button_layout)
        console_layout.add_widget(topBar)

        self.console = TextInput(readonly=True, foreground_color=(1,1,1,1), background_color=(0.1,0.1,0.1,1), size_hint=(1, 0.5), font_size=18, scroll_y=0)
        console_layout.add_widget(self.console)
        
        self.command_input = TextInput(hint_text="status", font_size=16, multiline=False, write_tab=False, on_text_validate=self.rcon_command, size_hint_y=0.035)
        self.command_input.text_validate_unfocus = False
        console_layout.add_widget(self.command_input)

        button = Button(text='Send', font_name="myfont", size_hint=(1, 0.05), font_size=18)
        button.bind(on_press=self.rcon_command)
        self.console.bind(on_touch_down=self.clear_selection)
        
        console_layout.add_widget(button)

        sys.stdout = self
        sys.stderr = self

        return console_layout

    def clear_selection(self, instance, touch):
        if self.console.collide_point(*touch.pos):
            self.console.cancel_selection()

    def write(self, msg):
        Clock.schedule_once(lambda dt: self.update_console(msg))
    
    def update_console(self, msg):
        self.console.text += msg
    
    def clear_field(self, element):
        element.text = ""
    def settext(self, field, txt):
        try:
            if isinstance(txt, str):
                field.text = txt
                field.focus = True
                field.focused = True
            else:
                print("txt is not a string")
        except Exception as e:
            print(e)
        

    def flush(self):
        pass

    def rcon_command(self, instance):
        threading.Thread(target=self.execute_rcon_command).start()
    
    def save_new_server(self, instance):
        if len(self.name_input.text) < 1:
            return
        if len(self.ip_input.text) < 10:
            return
        if len(self.pass_input.text) < 4 :
            return
        
        try:
            savedServers = loadSavedServers()
            if isinstance(savedServers, dict):
                savedServers[self.name_input.text] = {
                    "ip": self.ip_input.text,
                    "rcon_pass": self.pass_input.text
                }
            else:
                savedServers = {}
                savedServers[self.name_input.text] = {
                    "ip": self.ip_input.text,
                    "rcon_pass": self.pass_input.text
                }
            saveServers(savedServers)
            
            self.settings_popup.dismiss()
        except Exception as e:
            print(e)
    
    def deleteModeON(self, instance):
        self.deletemode = True
    
    def srv_btn_action(self, instance, text1, text2, text3):
        if self.deletemode:
            try:
                savedServers = loadSavedServers()
                savedServers.pop(text3)
                rewriteServers(savedServers)
            except Exception as e:
                print(e)
        else:
            try:
                global server_ip, server_port, rcon_password
                ip_port = splitstr(":", text1)
                server_ip = ip_port[0]
                server_port = int(ip_port[1])
                rcon_password = text2
                self.servers_popup.dismiss()
            except Exception as e:
                print(e)
        
    def show_servers(self, instance):
        try:
            savedServers = loadSavedServers()
            self.deletemode = False
            server_list = ScrollView()
            list_layout = StackLayout(size_hint_y=None, spacing=3, padding=2)
            list_layout.bind(minimum_height=list_layout.setter('height'))
            if isinstance(savedServers, dict):
                for server in savedServers:
                    server_btn = Button(text=server, size_hint=(randomFloatRange(0.2,0.3),None), height=dp(80), font_name="myfont")
                    server_btn.ip = savedServers[server].get('ip')
                    server_btn.rcon_pass = savedServers[server].get('rcon_pass')
                    server_btn.bind(on_press=partial(self.srv_btn_action, text1=server_btn.ip, text2=server_btn.rcon_pass, text3=server))
                    list_layout.add_widget(server_btn)
            
            new_srv_btn = Button(text="+", opacity=0.5, font_size=48, size_hint=(0.2,None), height=dp(80))
            new_srv_btn.bind(on_press=self.show_settings_popup)
            del_srv_btn = Button(text="-", opacity=0.5, font_size=48, size_hint=(0.2,None), height=dp(80))
            del_srv_btn.bind(on_press=self.deleteModeON)
            list_layout.add_widget(new_srv_btn)
            list_layout.add_widget(del_srv_btn)
            server_list.add_widget(list_layout)
            self.servers_popup = Popup(title="Saved Servers", size_hint=(0.8,0.8), content=server_list, title_align='center', title_size='16sp')
            self.servers_popup.open()
        except Exception as e:
            print(e)

    def show_settings_popup(self, instance):
        try:
            popup_layout = BoxLayout(orientation='vertical', spacing=5)
            name_text = Label(text="Server Name", font_size=18, size_hint_y=0.01)
            self.name_input = TextInput(multiline=False, write_tab=False, font_size=16, size_hint_y=0.01)
            ip_text = Label(text="IP Address:Port", font_size=18, size_hint_y=0.01)
            self.ip_input = TextInput(multiline=False, write_tab=False, font_size=16, size_hint_y=0.01)
            pass_text = Label(text="RCON Password", font_size=18, size_hint_y=0.01)
            self.pass_input = TextInput(password=True, multiline=False, write_tab=False, on_text_validate=self.save_new_server, font_size=16, size_hint_y=0.01)
            
            save_button = Button(text="Save", font_name="myfont", size_hint_y=0.01)
            save_button.bind(on_press=self.save_new_server)
            
            popup_layout.add_widget(name_text)
            popup_layout.add_widget(self.name_input)
            popup_layout.add_widget(ip_text)
            popup_layout.add_widget(self.ip_input)
            popup_layout.add_widget(pass_text)
            popup_layout.add_widget(self.pass_input)
            popup_layout.add_widget(save_button)
            
            self.settings_popup = Popup(title="Settings", size_hint=(0.6,0.6), content=popup_layout)
            self.settings_popup.open()
        except Exception as e:
            print(e)

    def execute_rcon_command(self):
        if self.command_input.text == "clear":
            Clock.schedule_once(lambda dt: self.clear_field(self.console))
            Clock.schedule_once(lambda dt: self.clear_field(self.command_input))
            return
        Clock.schedule_once(lambda dt: self.clear_field(self.command_input))
        response = rcon_command(server_ip, server_port, rcon_password, command=self.command_input.text)
        self.write(response + '\n')
    
    def getMapList(self):
        maps = []
        cmd = "sv_maprotation"
        response = rcon_command(server_ip, server_port, rcon_password, command=cmd)
        if splitstr(" ", response)[0] != "Failed":
            arr = splitstr('"', response)
            maps = (splitstr(" map ", arr[3]))
            maps.__delitem__(0)
            maps[-1] = monotone(maps[-1])
            """for map in maps:
                print(map)"""
            self.maps = maps
            self.maps_popup.dismiss()
        else:
            print(response)
        #return maps
    
    def maplist(self, instance):
        try:
            threading.Thread(target=self.getMapList).start()
            sleep(0.5)
            self.show_maplist(instance)
        except Exception as e:
            print(e)
    
    def changeMap(self, instance, map):
        try:
            txt = "map " + map
            Clock.schedule_once(lambda dt: self.settext(self.command_input, txt))
            self.maps_popup.dismiss()
        except Exception as e:
            print(e)
    
    def show_maplist(self, instance):
        try:
            maps = self.maps
            list_layout = ScrollView()
            maps_layout = StackLayout(size_hint_y=None, spacing=3, padding=2)
            maps_layout.bind(minimum_height=maps_layout.setter('height'))
            #if isinstance(maps, list):
            for map in maps:
                map_btn = Button(text=map, font_name="myfont", size_hint=(0.3,None), height=dp(140))
                map_btn.bind(on_press=partial(self.changeMap, map=map))
                maps_layout.add_widget(map_btn)
            refresh_maps = Button(text="↻", font_name="dejavu", font_size=56, size_hint=(0.3,None), height=dp(140))
            refresh_maps.bind(on_press=self.maplist)
            maps_layout.add_widget(refresh_maps)
            list_layout.add_widget(maps_layout)
            self.maps_popup = Popup(title="Maps", size_hint=(0.8, 0.8), content=list_layout)
            self.maps_popup.open()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    LabelBase.register(name="myfont", fn_regular=myFont)
    LabelBase.register(name="dejavu", fn_regular=dejavu)
    CoYoTeApp().run()
