import time
import threading
import traceback
from typing import List, Dict, Optional, Callable

import comtypes
from comtypes import GUID, COMMETHOD, HRESULT
from ctypes import POINTER, c_float, c_uint32
from ctypes.wintypes import DWORD
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioMeterInformation

# COM Interface for per-channel volume control (WASAPI)
class IChannelAudioVolume(comtypes.IUnknown):
    _iid_ = GUID('{1C158861-B533-4B30-B1CF-E853E51C59B8}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'GetChannelCount',
                  (['out'], POINTER(DWORD), 'pdwCount')),
        COMMETHOD([], HRESULT, 'SetChannelVolume',
                  (['in'], DWORD, 'dwIndex'),
                  (['in'], c_float, 'fLevel'),
                  (['in'], POINTER(GUID), 'EventContext')),
        COMMETHOD([], HRESULT, 'GetChannelVolume',
                  (['in'], DWORD, 'dwIndex'),
                  (['out'], POINTER(c_float), 'pfLevel')),
        COMMETHOD([], HRESULT, 'SetAllVolumes',
                  (['in'], DWORD, 'dwCount'),
                  (['in'], POINTER(c_float), 'pfVolumes'),
                  (['in'], POINTER(GUID), 'EventContext')),
        COMMETHOD([], HRESULT, 'GetAllVolumes',
                  (['in'], DWORD, 'dwCount'),
                  (['out'], POINTER(c_float), 'pfVolumes')),
    ]


class AudioDuckerEngine:
    def __init__(self):
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None

        # Base Configuration Settings
        self.lecture_process_name: Optional[str] = None
        self.threshold: float = 0.02       # Peak volume sensitivity (0.005 - 0.30)
        self.ducked_volume: float = 0.15   # Spotify volume when lecture speaker talks (0.0 - 1.0)
        self.normal_volume: float = 0.85   # Spotify volume during silence (0.0 - 1.0)
        self.hold_time: float = 1.2        # Delay in seconds to keep ducked after speaker stops
        self.fade_speed: float = 0.25      # Fading interpolation factor per frame

        # Spatial Left-Ear Panning Feature
        self.left_ear_panning_enabled: bool = True  # Shift Spotify to Left Ear when ducked

        # Progressive Focus Ramp-Down Feature (ADHD Attention Span Builder)
        self.ramp_enabled: bool = False
        self.ramp_duration_minutes: float = 30.0  # Duration over which music fades to 0
        self.ramp_start_time: Optional[float] = None

        # Engine State
        self.current_peak: float = 0.0
        self.is_ducked: bool = False
        self.spotify_found: bool = False
        self.lecture_found: bool = False
        self.status_message: str = "Idle"
        
        # Callbacks for GUI updates
        self.on_update_callback: Optional[Callable[[Dict], None]] = None

        self._last_speech_time: float = 0.0

    @staticmethod
    def get_audio_sessions_info() -> List[Dict[str, str]]:
        """Returns a list of active applications currently registered with Windows Audio Session Manager."""
        comtypes.CoInitialize()
        apps = []
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process:
                    name = session.Process.name()
                    pid = session.ProcessId
                    if name and name.lower() not in ["system", "svchost.exe", "audiodg.exe"]:
                        apps.append({
                            "name": name,
                            "display_name": f"{name} (PID: {pid})"
                        })
        except Exception as e:
            print(f"Error fetching audio sessions: {e}")
        finally:
            comtypes.CoUninitialize()
        
        seen = set()
        unique_apps = []
        for app in apps:
            pname = app["name"].lower()
            if pname not in seen:
                seen.add(pname)
                unique_apps.append(app)
        return sorted(unique_apps, key=lambda x: x["name"].lower())

    def start(self, lecture_process_name: str, callback: Optional[Callable[[Dict], None]] = None):
        """Start the auto-ducking background thread."""
        if self.running:
            self.stop()
        self.lecture_process_name = lecture_process_name.lower()
        self.on_update_callback = callback
        self.ramp_start_time = time.time()
        self.running = True
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        """Stop the auto-ducking background thread."""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        self.status_message = "Stopped"

    def _run_loop(self):
        """Main WASAPI monitoring, spatial panning, volume control, and focus ramp-down loop."""
        comtypes.CoInitialize()
        try:
            while self.running:
                loop_start = time.time()
                sessions = AudioUtilities.GetAllSessions()
                
                lecture_sessions = []
                spotify_sessions = []

                for session in sessions:
                    if session.Process:
                        pname = session.Process.name().lower()
                        if self.lecture_process_name and (self.lecture_process_name in pname or pname in self.lecture_process_name):
                            lecture_sessions.append(session)
                        if "spotify" in pname:
                            spotify_sessions.append(session)

                self.lecture_found = len(lecture_sessions) > 0
                self.spotify_found = len(spotify_sessions) > 0

                max_peak = 0.0

                # 1. Check MAX peak level across ALL matching lecture sessions
                for l_session in lecture_sessions:
                    try:
                        meter = l_session._ctl.QueryInterface(IAudioMeterInformation)
                        peak_val = meter.GetPeakValue()
                        if peak_val > max_peak:
                            max_peak = peak_val
                    except Exception:
                        pass

                self.current_peak = max_peak

                # 2. Speech detection & ducking logic
                now = time.time()
                if max_peak >= self.threshold:
                    self._last_speech_time = now
                    self.is_ducked = True
                else:
                    if now - self._last_speech_time > self.hold_time:
                        self.is_ducked = False

                # 3. Calculate Progressive Focus Ramp-Down multiplier
                ramp_multiplier = 1.0
                time_remaining_str = ""
                ramp_progress_pct = 0.0

                if self.ramp_enabled and self.ramp_start_time:
                    elapsed = now - self.ramp_start_time
                    total_ramp_sec = self.ramp_duration_minutes * 60.0
                    
                    if total_ramp_sec > 0:
                        ramp_progress_pct = min(1.0, elapsed / total_ramp_sec)
                        ramp_multiplier = max(0.0, 1.0 - ramp_progress_pct)
                        
                        remaining_sec = max(0, int(total_ramp_sec - elapsed))
                        rem_m, rem_s = divmod(remaining_sec, 60)
                        time_remaining_str = f"{rem_m:02d}:{rem_s:02d}"

                # Calculate scaled target volumes
                effective_ducked = self.ducked_volume * ramp_multiplier
                effective_normal = self.normal_volume * ramp_multiplier

                # Determine target left and right channel volumes
                if self.is_ducked:
                    if self.left_ear_panning_enabled:
                        target_left = effective_ducked
                        target_right = 0.0  # Mute Right ear when ducked so right ear focuses 100% on lecture!
                    else:
                        target_left = effective_ducked
                        target_right = effective_ducked
                else:
                    target_left = effective_normal
                    target_right = effective_normal

                # 4. Apply smooth per-channel volume change to Spotify sessions
                for s_session in spotify_sessions:
                    try:
                        # Reset Master Volume to 1.0 so channel volumes govern actual volume level directly
                        master_vol_ctrl = s_session.SimpleAudioVolume
                        if abs(master_vol_ctrl.GetMasterVolume() - 1.0) > 0.01:
                            master_vol_ctrl.SetMasterVolume(1.0, None)

                        chan_control = s_session._ctl.QueryInterface(IChannelAudioVolume)
                        chan_count = chan_control.GetChannelCount()
                        
                        if chan_count >= 2:
                            cur_left = chan_control.GetChannelVolume(0)
                            cur_right = chan_control.GetChannelVolume(1)

                            new_left = cur_left + (target_left - cur_left) * self.fade_speed
                            new_right = cur_right + (target_right - cur_right) * self.fade_speed

                            new_left = max(0.0, min(1.0, new_left))
                            new_right = max(0.0, min(1.0, new_right))

                            if abs(new_left - cur_left) > 0.001 or abs(new_right - cur_right) > 0.001:
                                chan_control.SetChannelVolume(0, new_left, None)
                                chan_control.SetChannelVolume(1, new_right, None)
                        else:
                            master_vol_ctrl.SetMasterVolume(target_left, None)
                    except Exception as e:
                        try:
                            volume_control = s_session.SimpleAudioVolume
                            volume_control.SetMasterVolume(target_left, None)
                        except Exception:
                            pass

                # Build status message
                if not self.lecture_found:
                    self.status_message = f"Waiting for {self.lecture_process_name} (play sound in tab)..."
                elif not self.spotify_found:
                    self.status_message = "Lecture detected! Please start playing music on Spotify..."
                elif self.is_ducked:
                    pan_str = "LEFT EAR ONLY" if self.left_ear_panning_enabled else "STEREO"
                    self.status_message = f"🔊 SPEECH (Peak: {max_peak:.2f}) → Spotify DUCKED ({pan_str} | L:{int(target_left*100)}% R:{int(target_right*100)}%)"
                else:
                    self.status_message = f"🔇 SILENCE (Peak: {max_peak:.2f}) → Spotify STEREO NORMAL ({int(target_left*100)}%)"

                # Send feedback to GUI callback
                if self.on_update_callback:
                    state_info = {
                        "peak": self.current_peak,
                        "is_ducked": self.is_ducked,
                        "lecture_found": self.lecture_found,
                        "spotify_found": self.spotify_found,
                        "status": self.status_message,
                        "target_left": target_left,
                        "target_right": target_right,
                        "ramp_multiplier": ramp_multiplier,
                        "ramp_progress_pct": ramp_progress_pct,
                        "time_remaining_str": time_remaining_str
                    }
                    try:
                        self.on_update_callback(state_info)
                    except Exception:
                        pass

                # Sleep for ~30ms loop interval
                elapsed_loop = time.time() - loop_start
                sleep_dur = max(0.005, 0.033 - elapsed_loop)
                time.sleep(sleep_dur)

        except Exception as e:
            print(f"Engine thread error: {e}")
            traceback.print_exc()
        finally:
            comtypes.CoUninitialize()
            self.running = False
