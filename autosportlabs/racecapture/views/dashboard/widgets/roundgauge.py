import kivy
kivy.require('1.8.0')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import Builder
from kivy.metrics import dp
from autosportlabs.racecapture.views.dashboard.widgets.fontgraphicalgauge import FontGraphicalGauge
from utils import kvFind

Builder.load_file('autosportlabs/racecapture/views/dashboard/widgets/roundgauge.kv')

from kivy.uix.image import Image
class IndexedImage(Image):
    
    def __init__(self, **kwargs):
        super(IndexedImage, self).__init__(**kwargs)

        
    def anim_index(self, index):
        self.anim_delay = -1      
        coreimage = self._coreimage
        if not coreimage._image:
            return
        textures = self._coreimage.image.textures
        if index >= len(textures) or index < 0:
            index = 0

        coreimage._anim_index = index
        coreimage._texture = coreimage.image.textures[index]
        self.texture = self._coreimage.texture

class RoundGauge(FontGraphicalGauge):
    
    def __init__(self, **kwargs):
        super(RoundGauge, self).__init__(**kwargs)
        self.initWidgets()
            
    def initWidgets(self):
        pass
    
    def on_channel(self, instance, value):
        addChannelView = self.ids.get('add_gauge')
        if addChannelView: addChannelView.text = '+' if value == None else ''
        return super(RoundGauge, self).on_channel(instance, value)    