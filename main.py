import sys, traceback
from pathlib import Path
import ffmpeg
import os
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QProgressBar, QCheckBox
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets
from pytube import YouTube
from PyQt6.QtGui import *
from threading import *


youtubeDirVid = ""
fileSizeVid = 0
ytTitleVideo = ""
ytTitleVidReal = ""
checkBoxHDState = False
checkBox720State = False

youtubeDirMus = ""
fileSizeMus = 0
ytTitleMus = ""
ytTitleMusReal = ""


class MergeAudioVideoThread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(MergeAudioVideoThread ,self).__init__()
    
    def __del__(self):
        self.wait()

    def run(self):
        

        downloadDirectoryMp3 = str(Path.home() / "Downloads") + '/video.mp3'
        downloadDirectoryMp4 = str(Path.home() / "Downloads") + '/video.mp4'
        downloadDirectoryFinal = str(Path.home() / "Downloads") + '/video-final.mp4'

        video_stream = ffmpeg.input(downloadDirectoryMp4)
        audio_stream = ffmpeg.input(downloadDirectoryMp3)
        ffmpeg.concat(video_stream, audio_stream, v=1, a=1).output(downloadDirectoryFinal).run()

        os.remove(downloadDirectoryMp3)
        os.remove(downloadDirectoryMp4)

        self._signal.emit(1)




class YtMusicDwnThread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(YtMusicDwnThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):
        global youtubeDirMus
        global fileSizeMus
        global ytTitleMus
        global checkBoxHDState
        global ytTitleMusReal

        directoryDir = str(Path.home() / "Downloads")

        # url input from user
        yt = YouTube(
            str(youtubeDirMus),on_progress_callback=self.progress_func)

        ytTitleMus = yt.title
        
        
        
        # extract only audio
        video = yt.streams.filter(only_audio=True,bitrate="160kbps")[0]
        fileSizeMus = video.filesize

        
        destination = directoryDir
        
        # download the file
        out_file = video.download(output_path=destination)
        
        if checkBoxHDState == True:
            base, ext = os.path.splitext(out_file)
            ytTitleMusReal = base
            new_file = str(Path.home() / "Downloads") + '/' + 'video.mp3'
            os.rename(out_file, new_file)
        else:
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
       

    
    def progress_func(self, stream, chunk, bytes_remaining):
        global fileSizeMus
        bytes_downloaded = fileSizeMus - bytes_remaining 
        percentage_of_completion = bytes_downloaded / fileSizeMus * 100
        self._signal.emit(int(percentage_of_completion))


        
        


class YtVideoDwnThread(QThread):
    _signal = pyqtSignal(int)
    def __init__(self):
        super(YtVideoDwnThread, self).__init__()

    def __del__(self):
        self.wait()

    def run(self):

        global fileSizeVid
        global youtubeDirVid
        global ytTitleVideo
        global checkBoxHDState
        global ytTitleVidReal

        
        directoryDir = str(Path.home() / "Downloads")

        # url input from user
        yt = YouTube(
            str(youtubeDirVid), on_progress_callback=self.progress_func)
        
        #ytTitleVideo = yt.title
        ytTitleVideo = 'video'
        ytTitleVidReal = yt.title

        # extract video in highest resolution
        if checkBoxHDState:
            video = yt.streams.filter(file_extension='mp4', adaptive="True", res = "1080p").first()
        else:
            video = yt.streams.get_highest_resolution()
        #
        fileSizeVid = video.filesize
        # check for destination to save file
        #print("Enter the destination (leave blank for current directory)")
        destination = directoryDir
        
        # download the file
        out_file = video.download(output_path=destination)
        
        if checkBoxHDState == True:
            new_file = str(Path.home() / "Downloads") + '/' + 'video.mp4'
            os.rename(out_file, new_file)
        else:
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp4'
            os.rename(out_file, new_file)
        
       

    def progress_func(self, stream, chunk, bytes_remaining):
        global fileSizeVid
        bytes_downloaded = fileSizeVid - bytes_remaining 
        percentage_of_completion = bytes_downloaded / fileSizeVid * 100
        self._signal.emit(int(percentage_of_completion))
        
    
class MyApp(QWidget):
 
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle('YouTube music and video downloader')
        self.setWindowIcon(QIcon('YT_icon'))
        self.resize(600, 500)

        layoutMain = QVBoxLayout()
        layoutMusic = QVBoxLayout()
        layoutVideo = QVBoxLayout()
        layoutDefinition = QHBoxLayout()
        self.setLayout(layoutMain)

        # widgets
        messageInputMp3Link = QtWidgets.QLabel("Music mp3 downloader")
        messageInputMp3LinkInst = QtWidgets.QLabel("Enter the video link:")
        self.inputMusicField = QLineEdit()
        self.pbarMus = QProgressBar(self)
        self.pbarMus.setValue(0)
        self.buttonDownloadMusic = QPushButton('&Download', clicked=self.threadStartDownMus)

        messageInputVideoLink = QtWidgets.QLabel("Video mp4 downloader")
        messageInputVideoLinkInst = QtWidgets.QLabel("Enter the video link:")
        self.inputVideoField = QLineEdit()
        self.checkBoxVideo720 = QCheckBox('720p')
        self.checkBoxVideo1080 = QCheckBox('1080p')
        self.pbar = QProgressBar(self)
        self.pbar.setValue(0)
        self.buttonDownloadVideo = QPushButton('&Download', clicked = self.checkValidQualSelection)

        self.checkBoxVideo720.toggled.connect(self.set720CheckBoxState)
        self.checkBoxVideo1080.toggled.connect(self.setHDCheckboxState)
        layoutDefinition.addWidget(self.checkBoxVideo720)
        layoutDefinition.addWidget(self.checkBoxVideo1080)

        layoutMusic.addWidget(messageInputMp3Link)
        layoutMusic.addWidget(messageInputMp3LinkInst)
        layoutMusic.addWidget(self.inputMusicField)
        layoutMusic.addWidget(self.pbarMus)
        layoutMusic.addWidget(self.buttonDownloadMusic)

        layoutMain.addLayout(layoutMusic)

        layoutVideo.addWidget(messageInputVideoLink)
        layoutVideo.addWidget(messageInputVideoLinkInst)
        layoutVideo.addWidget(self.inputVideoField)
        layoutVideo.addLayout(layoutDefinition)
        layoutVideo.addWidget(self.pbar)
        layoutVideo.addWidget(self.buttonDownloadVideo)
        

        layoutMain.addLayout(layoutVideo)
        layoutMusic.setContentsMargins(0,0,0,65)

    def checkValidQualSelection(self):
        global checkBox720State
        global checkBoxHDState

        if checkBoxHDState == False and checkBox720State == False:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Select a resolution")
            dlg.setText('Please select a resolution to download')
            dlg.exec()

        elif checkBoxHDState == True and checkBox720State == True:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Select just one resolution")
            dlg.setText('Please select just one resolution')
            dlg.exec()

        else:
            self.threadStartDownVid()

    def set720CheckBoxState(self):
        global checkBox720State
        checkBox720State = self.checkBoxVideo720.sender().isChecked()

    def setHDCheckboxState(self):
        global checkBoxHDState
        checkBoxHDState = self.checkBoxVideo1080.sender().isChecked()
            
    def threadStartDownVid(self):
        global checkBoxHDState
        global youtubeDirVid
        if checkBoxHDState:
            self.threadStartDownMus()
        if checkBoxHDState == False:
            self.buttonDownloadVideo.setEnabled(False)
        youtubeDirVid = self.inputVideoField.text()
        self.thread = YtVideoDwnThread()
        self.thread._signal.connect(self.signalAcceptDownVid)
        self.thread.start()
        

    def signalAcceptDownVid(self, msg):
        global ytTitleVidReal
        global checkBoxHDState
        self.pbar.setValue(int(msg))
        if self.pbar.value() == 100:
            if checkBoxHDState == False:
                self.buttonDownloadVideo.setEnabled(True)
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Download complete")
                dlg.setText(ytTitleVidReal + '.mp4' + ' is now in your Downloads folder.')
                dlg.exec()
            self.pbar.setValue(0)
            if checkBoxHDState == True:
                self.startMergeAudioVideo()

    def threadStartDownMus(self):
        global checkBoxHDState
        global youtubeDirMus
        if checkBoxHDState:
            youtubeDirMus = self.inputVideoField.text()
            self.thread = YtMusicDwnThread()
            self.thread._signal.connect(self.signalAcceptDownMus)
            self.thread.start()
            self.buttonDownloadVideo.setEnabled(False)
        else:
            youtubeDirMus = self.inputMusicField.text()
            self.thread = YtMusicDwnThread()
            self.thread._signal.connect(self.signalAcceptDownMus)
            self.thread.start()
            self.buttonDownloadMusic.setEnabled(False)

    def signalAcceptMerge(self, msg):
        global ytTitleMus
        global ytTitleMusReal
        self.buttonDownloadVideo.setEnabled(True)
        out_file = str(Path.home() / "Downloads") + '\\' + 'video-final.mp4'
        new_file = ytTitleMusReal + '.mp4'
        os.rename(out_file, new_file)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Download complete")
        dlg.setText(ytTitleMus + '.mp4' + ' is now in your Downloads folder.')
        dlg.exec()

    
    def startMergeAudioVideo(self):
        self.thread = MergeAudioVideoThread()
        self.thread._signal.connect(self.signalAcceptMerge)
        self.thread.start()

    def signalAcceptDownMus(self, msg):
        global ytTitleMus
        global checkBoxHDState
        if checkBoxHDState:
            self.pbar.setValue(int(msg))
        else:
            self.pbarMus.setValue(int(msg))
        if self.pbarMus.value() == 100:
            if checkBoxHDState:
                self.pbarMus.setValue(0)
            else:
                self.buttonDownloadMusic.setEnabled(True)
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Download complete")
                dlg.setText(ytTitleMus + '.mp3' + ' is now in your Downloads folder.')
                dlg.exec()
                self.pbarMus.setValue(0)

 

app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet('''
    QWidget {
        font-size: 15px;
    }
    QPushButton {
        font-size: 15px;
    }
''')

window = MyApp()
window.show()

sys.exit(app.exec())