Main = """
Screen:
    name: "Home"    

    Input:
        id: video
        hint_text: "Write the name here "
        x,y = 0.7, 0.75
        size_hint_x: 0.4
        on_text_validate: app.start()

    MDLabel:
        text: "Search any video by keywords"
        x,y = 0.53, 0.74
        font_size: 18


    Input:
        id: downloads
        hint_text: app.path
        x,y = 0.7, 0.57
        hint_text_font_size: 1
        size_hint_x: 0.4
        on_text: app.setPath(self.text)

    MDLabel:
        text: "Choose a path to save your video at"
        x,y = 0.53, 0.56
        font_size: 18

    BtnIcon:
        id: download_button
        text: "Search"
        icon: "web"
        x,y = 0.7, 0.3
        font_size: "20sp"
        md_bg_color: 30/255, 155/255, 227/255, 1
        text_color: 250/255, 250/255, 250/255, 1
        icon_color: 250/255, 250/255, 250/255, 1
        on_press: app.start()

    MDProgressBar:
        id: progress
        x, y = 0.3, 0.3
        size_hint_x: 0.4
        type: "indeterminate"
        running_duration: 0.7
        catching_duration: 0.7

    MDLabel:
        text: app.update
        pos_hint: {"center_y": 0.15}
        halign: 'center'
        font_size: "18sp"


Screen:
    name: 'download'

    Text:
        id: label_d
        x, y = 0.7, 0.77
        font_size: "18sp"
        font_size: 23
        size_hint_x: 0.5   
        font_name: 'arial' 

    MDLabel:
        id: c
        x, y = 0.3, 0.48
        font_size: "18sp"
        font_size: 22
        size_hint_x: 0.5
        font_name: 'arial' 

    Img:
        id: image
        x, y = 0.22, 0.7
        size_hint_x: 0.35
        opacity: 0

    MDLabel:
        x, y = 0.52, 0.36
        id: views
        font_size: 20

    MDLabel
        x, y = 0.52, 0.28
        id: duration
        font_size: 20

    MDLabel:
        x, y = 0.52, 0.2
        id: publish
        font_size: 20

    BoxLayout:
        orientation: "vertical"
        spacing: "10dp"
        id: mdcard
        size_hint: 0.6, 0.75
        x, y = 0.7, 0.33
        padding: 15
        ScrollView:
            MDList:
                id: container

    BtnIcon:
        id: open_button
        text: "Open"
        icon: "video-outline"
        x, y = 0.12, 0.08
        md_bg_color: 30/255, 155/255, 227/255, 1
        text_color: 250/255, 250/255, 250/255, 1
        icon_color: 250/255, 250/255, 250/255, 1
        on_press: app.startFile()

Screen: 
    name: 'search'

    BoxLayout:
        orientation: "vertical"
        spacing: "10dp"
        id: mdcard
        size_hint: 1, 1
        x, y = 0.5, 0.4
        padding: 15
        ScrollView:
            MDList:
                id: search
"""