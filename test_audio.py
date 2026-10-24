import comtypes
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from audio_engine import IChannelAudioVolume

comtypes.CoInitialize()
try:
    sessions = AudioUtilities.GetAllSessions()
    print(f"Found {len(sessions)} audio sessions:")
    for s in sessions:
        if s.Process:
            pname = s.Process.name()
            print(f"  - App: {pname} (PID: {s.ProcessId})")
            try:
                chan = s._ctl.QueryInterface(IChannelAudioVolume)
                count = chan.GetChannelCount()
                print(f"    Channels: {count}")
                if count >= 2:
                    l = chan.GetChannelVolume(0)
                    r = chan.GetChannelVolume(1)
                    print(f"    Left Vol: {l:.2f}, Right Vol: {r:.2f}")
            except Exception as e:
                print(f"    IChannelAudioVolume error: {e}")
                vol = s.SimpleAudioVolume
                print(f"    Master Vol: {vol.GetMasterVolume():.2f}")
finally:
    comtypes.CoUninitialize()
