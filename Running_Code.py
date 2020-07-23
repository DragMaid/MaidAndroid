#All the modules
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.theming import ThemeManager, ThemableBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.uix.list import OneLineAvatarListItem, OneLineAvatarIconListItem
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader
from kivymd.uix.list import ILeftBody
from kivy.uix.image import Image
from kivymd.uix.picker import MDDatePicker
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import CircularRippleBehavior
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
import PIL as pl
from PIL import ImageDraw
import numpy as np
from kivymd.toast import toast
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCardSwipe
from functools import partial

#For no drawing on Screen
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

#Data Base For User_Account 
store = JsonStore("Account.json")

#Screen Control Manager and the Screens 
class Login_Screen(Screen):

    account = ObjectProperty(None)

    def checking_proccess(self):
        x = len(self.account.text.strip())
        if x > 0:
            user_input = self.account.text.strip()
            root.current = "Navigation_Screen"
            self.manager.ids.Navigation_Screen.username = user_input
            store.clear()
            store.put('User_Profile', name = user_input)
        elif x <= 0:
            root.current = "Login_Screen"




class Navigation_Screen(Screen):
    username = StringProperty()
    calendar_time = StringProperty()
    date = ObjectProperty()
    first_input = ObjectProperty()
    second_input = ObjectProperty()
    third_input = ObjectProperty()
    avt_draw = ObjectProperty()
    avt_prev = ObjectProperty()
    tlist = ObjectProperty()
    taskNumber = NumericProperty(1)


    #Calendar Function`
    #With DataBase
    def open_calendar(self, *args):
        pd = self.date
        if len(self.calendar_time) > 0:
            try:
                MDDatePicker(self.set_previous_date,
                             year = int(self.calendar_time[0:4]),
                             month = int(self.calendar_time[5:7]),
                             day = int(self.calendar_time[8:10])
                             ).open()
 
            except AttributeError:
                MDDatePicker(self.set_previous_date).open()

        elif len(self.calendar_time) == 0:
            MDDatePicker(self.set_previous_date).open()

    def set_previous_date(self, date_obj):
        self.date = date_obj
        store.put('Selection', last_date = str(date_obj))
        self.calendar_time = str(store.get("Selection")['last_date'])


    #Goals show up
    def anime_run(self, widget1, widget2, widget3, *args):
        anim = Animation(third_pos = .6)
        anim2 = Animation(first_pos = .85)
        anim3 = Animation(second_pos = .7)
        anim.start(widget1)
        anim2.start(widget2)
        anim3.start(widget3)
        try:
            self.first_input.text = str(store.get('first_input')['text'])
            self.second_input.text = str(store.get('second_input')['text'])
            self.third_input.text = str(store.get('third_input')['text'])
        except:
            pass 
        self.update_text = Clock.schedule_interval(self.update_json, 20)

    def update_json(self, *args):
        if self.ids.screenmanager.current != "Goals_System":
            self.update_text.cancel()
        else:
            store.put("third_input", text=str(self.third_input.text))
            store.put("second_input", text=str(self.second_input.text))
            store.put("first_input", text=str(self.first_input.text))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            #previous=True,
        )

    def file_manager_open(self):
        self.file_manager.show('/')  
        self.manager_open = True

    def select_path(self, path):

        self.exit_manager()
        try: 
            self.crop_pic(path)
            self.update_avatar()
            toast("Avatar selected!")
        except:
            toast("Failed! Incorrect format!")

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def crop_pic(self, path): 
        im = pl.Image.open(path)

        new_size = im.resize((110,110))

        npImage=np.array(new_size)

        h,w= new_size.size

        alpha = pl.Image.new('L', new_size.size,0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0,0,h,w],0,360,fill=255)

        # Convert alpha Image to numpy array
        npAlpha=np.array(alpha)

        # Add alpha layer to RGB
        npImage=np.dstack((npImage,npAlpha))

        # Save with alpha
        pl.Image.fromarray(npImage).save("avatar.png")

    def update_avatar(self, *args): 
        self.avt_prev.reload() 
        self.avt_draw.reload()

    def Add_Task(self, taskname, *args):

        if len(taskname) == 0:
            self.tlist.add_widget(Task_Widget(text="Task {}".format(self.taskNumber)))
            self.text = "Task {}".format(self.taskNumber)
            self.save_task()
        else:
            self.tlist.add_widget(Task_Widget(text=taskname))
            self.text = taskname
            self.save_task()

        self.taskNumber += 1  

        self.set_name.dismiss()

    def save_task(self, *args):
        x = "Task{}".format(self.taskNumber)
        store.put(x, name = self.text)
        store.put('taskNumber', num = self.taskNumber)

    time_pressed = NumericProperty(0)
    
    def load_checkpoint(self, *args):
        if self.time_pressed == 0:
            try:
                num = store.get('taskNumber')['num']
                self.taskNumber = num + 1 
                for i in [x for x in range(num + 1) if x != 0]:

                    self.tlist.add_widget(Task_Widget(text=store.get("Task"+str(i))['name']))
                self.time_pressed += 1 
            except:
                pass 
        else:
            pass

    def show_set_name(self, *args):

        self.set_name = MDDialog(
            title="Configure your task!",
            type="custom",
            size_hint = [.6, .5],
            content_cls = Name_Conifigure(),
        ) 

        self.set_name.open()

    def remove_item(self, instance, name):
        self.tlist.remove_widget(instance)
        for item in store.find(name=name.text):
            self.new = (item[0])

        store.delete(self.new)

        store.put('taskNumber', num = store.get('taskNumber')['num'] - 1)


    def change_name_dialog(self, instance):
        self.new = instance
        self.name_change = MDDialog(
            title="Configure your task!",
            type="custom",
            size_hint = [.6, .5],
            content_cls = Change_Name(),
        )
        self.name_change.open()

    def change_name(self, taskname, *agrs):
        if len(taskname.strip()) == 0:
            pass
        else:
            for item in store.find(name=self.new.text):
                self.name = (item[0])

            store.put(self.name, name = taskname)

            self.new.text = taskname  

        self.name_change.dismiss()


class Name_Conifigure(FloatLayout):
    pass

class Change_Name(FloatLayout):
    pass 

class Main(Label):
    User_time = 60
    angle = NumericProperty(0)
    min, sec = divmod(User_time, 60)
    StopMusic = SoundLoader.load("Maid_Music/yu-zi-shi-chang-tamako-market-ed-ending-neguse.mp3")
    DISPLAY = StringProperty("{:02d}:{:02d}".format(min, sec))
    default_button_image = StringProperty("KivGUI picture/playButton.png")
    default_button_image2 = StringProperty("KivGUI picture/SettingIcon.png")
    new_min = ""
    new_sec = ""

    def start(self, *args):
        if self.default_button_image == "KivGUI picture/playButton.png":
            
            self.switch_to()
            self.CountDown()
            self.event = Clock.schedule_interval(self.CountDown, 1)
            self.Animate()
        else:
            self.reverse()
            self.pause()


    def pause(self):
        self.event.cancel()
        self.anime.cancel(self)

    def Animate(self):
        self.anime = Animation(angle=360, duration=self.User_time)
        self.anime.start(self)

    def CountDown(self, *args):
        self.DISPLAY = "{:02d}:{:02d}".format(self.min, self.sec)

        if self.DISPLAY == "00:00":
            self.StopMusic.play()
            self.reset()

        elif self.sec == 0:
            self.min -= 1
            self.sec = 59

        else:
            self.sec -= 1

    def setting_button_func(self):
        if self.default_button_image2 == "KivGUI picture/SettingIcon.png":
            self.select_dialog()
            #Worked on later

        else:
            self.reset()


    def reset(self):
        self.min, self.sec = divmod(self.User_time, 60)
        self.DISPLAY = "{:02d}:{:02d}".format(self.min, self.sec)
        self.reverse()
        self.pause()
        self.angle = 0

    def light_refresh(self):
        self.min, self.sec = divmod(self.User_time, 60)
        self.DISPLAY = "{:02d}:{:02d}".format(self.min, self.sec)
        self.angle = 0

    def switch_to(self):
        self.default_button_image = "KivGUI picture/PauseIcon.png"
        self.default_button_image2 = "KivGUI picture/ReloadIcon.png"

    def reverse(self):
        self.default_button_image = "KivGUI picture/playButton.png"
        self.default_button_image2 = "KivGUI picture/SettingIcon.png"


    def select_dialog(self, *args):
        button1 = MDFlatButton(text="Cancel")
        button2 = MDFlatButton(text="Save")
        button1.bind(on_press=self.forget)
        button2.bind(on_press=self.save_changes)
        self.dialog = MDDialog(
            title="Choose your time:",
            type="custom",
            size_hint=[.5,.5],
            content_cls=my_layout(),
            buttons=[
                button1, 
                button2
            ]

        )   
###fix later 

        self.dialog.open()

    def min_sort(self):
        for x in range (len(my_layout.new_min)):
            try:
                self.new_min += str(int(my_layout.new_min[x]))

            except:
                pass 

    def sec_sort(self):
        for y in range (len(my_layout.new_sec)):
            try:
                self.new_sec += str(int(my_layout.new_sec[y]))

            except:
                pass 

        
    def save_changes(self, *args):
        self.min_sort()
        self.sec_sort()
        if self.new_min == "":

            try:
                self.User_time = 0 + int(self.new_sec)
                self.light_refresh()
                self.forget()
            except:
                self.forget()


        elif self.new_sec == "":
            try:
                self.User_time =  int(self.new_min) * 60 + 0 
                self.light_refresh()
                self.forget()

            except:
                self.forget()

        else:
            self.User_time = int(self.new_min) * 60 + int(self.new_sec)
            self.light_refresh()
            self.forget()

    def forget(self, *args):
        self.dialog.dismiss()
        self.new_min = ""
        self.new_sec = ""
 

###Bind ok and cacel buttons 



class my_layout(FloatLayout):


    new_min = ""
    new_sec = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items_min = [{"text": f"{i} Minutes"} for i in range(151)]
        menu_items_sec = [{"text": f"{i} Secs"} for i in range(61)]
        self.menu_min = MDDropdownMenu(
            caller=self.ids.btn,
            items=menu_items_min,
            position="bottom",
            callback=self.set_item_min,
            width_mult=4,
        )

        self.menu_sec = MDDropdownMenu(
            caller=self.ids.btn2,
            items=menu_items_sec,
            position="bottom",
            callback=self.set_item_sec,
            width_mult=4,
        )      

    def set_item_min(self, instance_min):
        self.ids.btn.set_item(instance_min.text)
        self.mins_select_text = (instance_min.text)
        my_layout.new_min = str(instance_min.text)

    def set_item_sec(self, instance_sec):
        self.ids.btn2.set_item(instance_sec.text)
        self.secs_select_text = (instance_sec.text)
        my_layout.new_sec = str(instance_sec.text)



###Save current theme function needed!

#User's Icon Graphic
 
class Task_Widget(MDCardSwipe):
    text = StringProperty()

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass 

class AvatarSampleWidget(ILeftBody, Image):
    pass

#User's custom Button with Image 
class Custom_Image_Button(CircularRippleBehavior, ButtonBehavior, Image):
    pass

class GUI(ScreenManager):
    pass


#System import control

class Main_System(MDApp):

#Theme saving

    #Start when the App is launched
    def on_start(self):



        if store.exists('User_Profile'):
            root.current = "Navigation_Screen"
            root.ids.Navigation_Screen.ids.my_label.text = str(store.get('User_Profile')['name'])

        if store.exists('Selection'):
            root.ids.Navigation_Screen.calendar_time = str(store.get('Selection')['last_date'])



    #Theme and Title Manager
    def __init__(self, **kwargs):
        super().__init__(*kwargs)
        self.title = "Maid Chan"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.theme_pallete = "Blue"




    #File's Build System for KV path
    def build(self):
        #would be the GUI widget
        global root
        self.root = root = Builder.load_file("Game_LayoutMB.kv")




#Build Setup

if __name__ == "__main__":
    Main_System().run()
