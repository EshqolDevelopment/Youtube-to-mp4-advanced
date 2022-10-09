import base64, os.path, sys, pytube
from pathlib import Path
from tkinter import filedialog, Tk

from kivy.clock import mainthread
from kivy4 import *
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, OneLineAvatarIconListItem, ThreeLineAvatarIconListItem
from kiv import Main
from youtube_search import YoutubeSearch
import shutil
import moviepy.editor as moviepy
import urllib.request


root = Tk()
root.withdraw()


class Youtube(Kivy4):
    path = StringProperty("")
    update = StringProperty("")
    pathToOpen = None
    active = StringProperty("high")
    is_downloading = False
    converting = False


    @thread
    def on_start(self):
        self.path = self.getFile('download', str(Path.home() / "Downloads"))
        self.active = self.getFile('active', 'high')
        if not os.path.exists(f'{self.appdata_path}/images'):
            os.mkdir(f'{self.appdata_path}/images')

    def on_request_close(self, *args):
        try:
            shutil.rmtree(f'{self.appdata_path}/images', ignore_errors=True)

        except Exception as e:
            print(e)

        finally:
            sys.exit()

    @thread
    def setPath(self, x: str):
        if x.strip() == '':
            self.root.ids.downloads.hint_text = self.path
            self.setFile('download', self.path)

        else:
            self.root.ids.downloads.hint_text = x
            self.setFile('download', x)

    @thread
    def setOption(self, x: str):
        self.setFile('active', x)
        self.active = x

    @thread
    def start(self):
        try:
            self.root.ids.progress.start()
            self.update = "Searching for video..."
            txt = self.root.ids.video.text
            results = YoutubeSearch(txt).to_dict()
            self.root.ids.search.clear_widgets()
            i = 0

            for re in results:
                item = OneLineAvatarIconListItem(text=re['title'])
                item.add_widget(IconLeftWidget(icon="download", on_press=lambda a, b=re, c=i: self.download(b, c)))
                self.root.ids.search.add_widget(item)

                i += 1

            self.root.ids.screen_manager.current = 'search'
            self.root.ids.progress.stop()
            self.update = ""


        except Exception as e:
            print(e)
            self.update = 'Invalid URL'
            return self.root.ids.progress.stop()


    @thread
    def download(self, results, index):
        self.root.ids.screen_manager.current, recommended = 'download', True
        self.add_details(results)
        self.root.ids.container.clear_widgets()

        y = pytube.YouTube("https://www.youtube.com/" + results["url_suffix"]).streams

        stream = y.filter(progressive=True)
        audio_stream = y.filter(only_audio=True)
        scam = y.filter(progressive=False).order_by("resolution").last()

        lst = sorted(list(set([(x.resolution, x.fps) for x in stream])), key=lambda z: int(z[0].replace('p', '')))[::-1]
        audio = sorted(list(set([x.abr for x in audio_stream])), key=lambda z: int(z.replace('kbps', '')))[::-1]

        item = ThreeLineAvatarIconListItem(text=f"Resolution of {scam.resolution}", secondary_text=f"{scam.fps} fps",
                                           tertiary_text='Warning, this might the a while to download!')
        item.add_widget(IconLeftWidget(icon="download",
                                       on_press=lambda x, f=scam.resolution, r=scam.fps: self.download_video(r, f, y,
                                                                                                             scam=True)))
        self.root.ids.container.add_widget(item)

        for s in lst:
            res, fps = s
            if recommended and int(res.replace('p', '')) >= 360:
                recommended = False
                item = ThreeLineAvatarIconListItem(text=f"Resolution of {res}", secondary_text=f"{fps} fps",
                                                   tertiary_text='Recommended')

            else:
                item = TwoLineAvatarIconListItem(text=f"Resolution of {res}", secondary_text=f"{fps} fps")

            item.add_widget(
                IconLeftWidget(icon="download", on_press=lambda x, f=fps, r=res: self.download_video(r, f, stream)))
            self.root.ids.container.add_widget(item)

        for s in audio:
            item = OneLineAvatarIconListItem(text=f"Quality of {s}")
            item.add_widget(IconLeftWidget(icon="music", on_press=lambda x, a=s: self.download_video(a, audio_stream)))
            self.root.ids.container.add_widget(item)

    @thread
    def add_details(self, results):
        self.im(results['thumbnails'][0], base64.b32encode(results['title'].encode()).decode())
        self.root.ids.label_d.text = results['title']
        self.root.ids.views.text = results['views']
        self.root.ids.duration.text = 'Duration of ' + results['duration'] + ' minuets'
        self.root.ids.publish.text = 'Uploaded ' + str(results['publish_time'])
        self.root.ids.c.text = results['channel']

    @thread
    def download_video(self, *args, scam=False):
        stream: pytube.query.StreamQuery = args[-1]

        if len(args) == 3:
            if scam:
                fetch = stream.filter(progressive=False, file_extension='mp4').order_by("resolution").last()

            else:
                fetch = stream.filter(res=args[0], fps=args[1]).first()

            t = f'resolution: {fetch.resolution}, fps: {fetch.fps}, file size: {round(fetch.filesize / 1000000, 2)}Mb'

        else:
            fetch = stream.filter(abr=args[0]).first()
            t = f'quality: {fetch.abr}, file size: {round(fetch.filesize / 1000000, 2)}Mb'

        try:
            pathToSave = self.root.ids.downloads.hint_text
            self.setFile('download', pathToSave)

            self.root.ids.label_d.font_size = '20'
            self.is_downloading = True
            self.update_text(t, scam)

            self.pathToOpen = pathToSave + '/' + fetch.default_filename

            if scam:
                self.scam(stream, fetch, self.root.ids.downloads.hint_text)

            else:
                fetch.download(pathToSave)
                self.is_downloading = False


        except Exception as e:
            self.on_error(e)

    def scam(self, stream, fetch, path):
        filename, extension = fetch.default_filename.split('.')
        directory = self.appdata_path + '/temp dir'

        audio = f'{filename}_audio.{extension}'
        video = f'{filename}_video.{extension}'

        self.audio(stream, directory, audio)
        fetch.download(directory, filename=video)

        self.is_downloading = False
        self.converting = True

        while not os.path.exists(f'{directory}/{audio}'):
            pass

        clip = moviepy.VideoFileClip(f'{directory}/{video}')
        final = clip.set_audio(moviepy.AudioFileClip(f'{directory}/{audio}'))
        final.write_videofile(f'{path}/{fetch.default_filename}')

        self.converting = False
        shutil.rmtree(directory, ignore_errors=True)

    @thread
    def audio(self, stream, path, filename):
        stream.get_audio_only().download(path, filename=filename)

    @thread
    def update_text(self, text, scam=False):
        a = ''

        if scam:
            while self.is_downloading:
                if a == '...':
                    a = ''

                a += '.'
                self.root.ids.label_d.text = f'Converting your file{a}\n\n{text}'
                time.sleep(0.8)

            while self.converting:
                if a == '...':
                    a = ''

                a += '.'
                self.root.ids.label_d.text = f'Downloading, it might take a while{a}\n\n{text}'
                time.sleep(0.8)

        else:
            while self.is_downloading:
                if a == '...':
                    a = ''

                a += '.'
                self.root.ids.label_d.text = f'Downloading{a}\n\n{text}'
                time.sleep(0.7)

        self.root.ids.label_d.text = 'Successfully downloaded!'

    def on_error(self, e):
        print(e)
        if repr(e) == "RegexMatchError('get_throttling_function_name: could not find match for multiple')":
            self.update = 'We could not download your video because of an update\nin YouTube, check for updates in Microsoft store until\nwe will fix it!'

        else:
            self.update = 'unexpected error'

    def folder(self):
        save_path = filedialog.askdirectory()

        if save_path is not None:
            self.root.ids.downloads.text = save_path
            self.setFile('download', save_path)

    @thread
    def startFile(self):
        if self.pathToOpen is None:
            return False

        os.startfile(self.pathToOpen)

    @thread
    def im(self, path, name):
        path_to_save = f'{self.appdata_path}/images/{name}.png'

        if path:
            urllib.request.urlretrieve(path, path_to_save)
            return self.update_image(name)

    @mainthread
    def update_image(self, name):
        self.root.ids.image.source = f'{self.appdata_path}/images/{name}.png'
        self.root.ids.image.opacity = 1

    def back(self):
        self.pathToOpen = None

        if self.root.ids.screen_manager.current == 'search':
            self.root.ids.screen_manager.current = 'Home'

        elif self.root.ids.screen_manager.current == 'download':
            self.root.ids.screen_manager.current = 'search'


if __name__ == '__main__':
    Youtube(icon="icon.png", string=Main, app_name="Youtube Downloader", main_color="Orange", screen_size=[0.45, 0.55],
            toolbar=['[[app.dark_mode_icon, lambda x: app.reverseDarkMode()]]',
                     '[["folder-outline", lambda x: app.folder(), "Choose a destiny folder"], ["arrow-left-circle", lambda x: app.back(), "Go back"]]',
                     "Download Songs and Videos from Youtube"]).run()
