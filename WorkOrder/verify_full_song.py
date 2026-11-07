"""Audio completion, playback clock and cancellation checks without audio hardware."""
import os
import sys
import tempfile
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import soundfile as sf
from app.audio.audio_player import AudioPlayer
from app.game.rhythm_game_engine import RhythmGameEngine
from app.audio.note_generator_adapter import chart_to_motion_notes
from app.ui.game_widget import GameWidget

with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/'entire_song.wav'
    sf.write(path,np.zeros(24000,dtype=np.float32),8000)
    started=threading.Event(); done=threading.Event()
    class Device:
        def play(self,data,rate,blocking):
            assert len(data)==24000 and rate==8000 and data.shape==(24000,2)
            started.set()
        def wait(self):
            assert done.wait(3)
        def stop(self): done.set()
    with patch.dict(sys.modules,{'sounddevice':Device()}):
        player=AudioPlayer(str(path)); player.play()
        assert started.wait(3)
        assert player.duration_seconds==3 and not player.finished and not player.loading
        assert player.started_at is not None
        done.set(); player._thread.join(3)
        assert player.finished and not player.error
    # Stop during decoding must not start playback later in the background.
    entered=threading.Event(); release=threading.Event()
    def delayed_decode():
        entered.set(); assert release.wait(3)
        return np.zeros(8000,dtype=np.float32),8000
    device=SimpleNamespace(play=lambda *a,**k: (_ for _ in ()).throw(AssertionError('stale audio started')),stop=lambda:None)
    with patch.dict(sys.modules,{'sounddevice':device}):
        player=AudioPlayer(str(path))
        with patch.object(player,'_load_audio',side_effect=delayed_decode):
            player.play(); assert entered.wait(3); assert player.loading
            player.stop(); release.set(); player._thread.join(3)
        assert player.finished and player.started_at is None and player.error is None

engine=RhythmGameEngine()
for note in engine.notes: note.judged=True
assert engine.is_finished(203000)
audio=SimpleNamespace(error=None,finished=False,position_ms=203000)
game=SimpleNamespace(song_path='214_seconds.mp3',audio_player=audio,engine=engine,start_time=0)
assert not GameWidget._should_finish(game,203000)
assert GameWidget._playback_time_ms(game)==203000
audio.position_ms=213770; audio.finished=True
assert GameWidget._should_finish(game,213770)
game.song_path=None
assert GameWidget._should_finish(game,203000)
assert RhythmGameEngine.normalize_note_dict({'hit_time_ms':500},0).hit_time_ms==500
assert RhythmGameEngine.normalize_note_dict({'time':.5},0).hit_time_ms==500
assert chart_to_motion_notes({'notes':[{'hit_time_ms':500,'lane':0}]})[0]['hit_time_ms']==500
print('PASS: full decoded track submitted; natural audio completion; no chart-based truncation; audio clock; sample mode; cancellation during loading; explicit millisecond timestamps')
