# -*- coding: utf-8 -*-
"""VoxBangla - Windows voice typing assistant (Bangla / English).

Speech transcription uses the Google Speech Recognition web service through
SpeechRecognition. Audio is sent over the internet for recognition.
"""
from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

APP_NAME = "VoxBangla Voice Typing"
APP_VERSION = "0.1.0"

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import pyperclip
except Exception:
    pyperclip = None

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    from bijoy_unicode import to_bijoy
except Exception:
    to_bijoy = None


class VoxBanglaApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(f"{APP_NAME}  •  v{APP_VERSION}")
        self.root.geometry("980x720")
        self.root.minsize(820, 620)
        self.root.configure(bg="#0b1220")

        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = None
        self.stop_listening = None
        self.active_language_code = "bn-BD"
        self.is_listening = False
        self.lock = threading.Lock()
        self.recognition_queue: queue.Queue[str] = queue.Queue()

        self.language_var = tk.StringVar(value="বাংলা (বাংলাদেশ)")
        self.output_var = tk.StringVar(value="Avro / Unicode")
        self.auto_insert_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="প্রস্তুত • মাইক্রোফোন চালু করতে Start চাপুন")
        self.level_var = tk.StringVar(value="মাইক্রোফোন: ডিফল্ট ডিভাইস")

        self._configure_style()
        self._build_ui()
        self._poll_queue()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def _configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#0b1220")
        style.configure("Panel.TFrame", background="#111c2f")
        style.configure("TLabel", background="#0b1220", foreground="#e5edf8", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#0b1220", foreground="#93a4bd", font=("Segoe UI", 9))
        style.configure("Panel.TLabel", background="#111c2f", foreground="#e5edf8", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0b1220", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        style.configure("SubTitle.TLabel", background="#0b1220", foreground="#9fb1cb", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.configure("Start.TButton", background="#16a36a", foreground="white")
        style.map("Start.TButton", background=[("active", "#128455"), ("disabled", "#365247")])
        style.configure("Stop.TButton", background="#c94b55", foreground="white")
        style.map("Stop.TButton", background=[("active", "#a93640"), ("disabled", "#563b41")])
        style.configure("Secondary.TButton", background="#24344c", foreground="#e5edf8")
        style.map("Secondary.TButton", background=[("active", "#314765")])
        style.configure("TCombobox", padding=7, fieldbackground="#17243a", background="#17243a", foreground="#f8fafc")
        style.map("TCombobox", fieldbackground=[("readonly", "#17243a")], foreground=[("readonly", "#f8fafc")])
        style.configure("TCheckbutton", background="#111c2f", foreground="#e5edf8", font=("Segoe UI", 10))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=24)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x")
        title_area = ttk.Frame(header)
        title_area.pack(side="left", fill="x", expand=True)
        ttk.Label(title_area, text="VoxBangla", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_area, text="বাংলা ও ইংরেজি ভয়েস টাইপিং • Windows 10 / 11", style="SubTitle.TLabel").pack(anchor="w", pady=(2, 0))
        self.status_dot = tk.Label(header, text="● OFF", bg="#0b1220", fg="#f59e0b", font=("Segoe UI", 10, "bold"))
        self.status_dot.pack(side="right", anchor="ne", pady=9)

        controls = ttk.Frame(outer, style="Panel.TFrame", padding=16)
        controls.pack(fill="x", pady=(20, 14))

        row1 = ttk.Frame(controls, style="Panel.TFrame")
        row1.pack(fill="x")
        ttk.Label(row1, text="ভাষা", style="Panel.TLabel").pack(side="left")
        lang = ttk.Combobox(row1, textvariable=self.language_var, state="readonly", width=24,
                            values=["বাংলা (বাংলাদেশ)", "English (US)"])
        lang.pack(side="left", padx=(10, 24))
        ttk.Label(row1, text="আউটপুট", style="Panel.TLabel").pack(side="left")
        output = ttk.Combobox(row1, textvariable=self.output_var, state="readonly", width=28,
                              values=["Avro / Unicode", "Bijoy Unicode", "Bijoy Classic (ANSI)"])
        output.pack(side="left", padx=(10, 0))

        row2 = ttk.Frame(controls, style="Panel.TFrame")
        row2.pack(fill="x", pady=(15, 0))
        self.start_button = ttk.Button(row2, text="●  START VOICE TYPING", style="Start.TButton", command=self.start_listening)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(row2, text="■  STOP", style="Stop.TButton", command=self.stop_recording, state="disabled")
        self.stop_button.pack(side="left", padx=(10, 0))
        ttk.Checkbutton(row2, text="সক্রিয় উইন্ডোতে সরাসরি টাইপ করবে", variable=self.auto_insert_var).pack(side="left", padx=(22, 0))

        status_panel = ttk.Frame(outer, style="Panel.TFrame", padding=(14, 10))
        status_panel.pack(fill="x", pady=(0, 14))
        ttk.Label(status_panel, textvariable=self.status_var, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(status_panel, textvariable=self.level_var, style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

        text_header = ttk.Frame(outer)
        text_header.pack(fill="x", pady=(2, 8))
        ttk.Label(text_header, text="ট্রান্সক্রিপশন / সম্পাদনাযোগ্য লেখা", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Label(text_header, text="ভয়েস থেকে পাওয়া লেখা এখানে দেখা যাবে", style="Muted.TLabel").pack(side="right")

        text_frame = tk.Frame(outer, bg="#26364e", padx=1, pady=1)
        text_frame.pack(fill="both", expand=True)
        self.text_box = tk.Text(text_frame, wrap="word", undo=True, bg="#101a2b", fg="#edf4ff",
                                insertbackground="#ffffff", selectbackground="#245e88", relief="flat",
                                padx=16, pady=14, font=("Nirmala UI", 13), spacing1=3, spacing3=5)
        self.text_box.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(text_frame, command=self.text_box.yview)
        scroll.pack(side="right", fill="y")
        self.text_box.configure(yscrollcommand=scroll.set)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text="নির্বাচিত / সব লেখা পেস্ট", style="Secondary.TButton", command=self.paste_manual).pack(side="left")
        ttk.Button(actions, text="ক্লিপবোর্ডে কপি", style="Secondary.TButton", command=self.copy_text).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="TXT সংরক্ষণ", style="Secondary.TButton", command=self.save_text).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="মুছে ফেলুন", style="Secondary.TButton", command=self.clear_text).pack(side="right")

        footer = ttk.Label(outer,
            text="টিপস: Start চাপার পর Word/Notepad-এ কার্সর রাখুন। ANSI মোডে SutonnyMJ/Bijoy ফন্ট ব্যবহার করুন।",
            style="Muted.TLabel", wraplength=900)
        footer.pack(anchor="w", pady=(12, 0))

    def _set_status(self, message: str, active: bool | None = None) -> None:
        self.status_var.set(message)
        if active is True:
            self.status_dot.configure(text="● LISTENING", fg="#34d399")
        elif active is False:
            self.status_dot.configure(text="● OFF", fg="#f59e0b")

    def start_listening(self) -> None:
        if self.is_listening:
            return
        if sr is None:
            messagebox.showerror("Dependency missing", "SpeechRecognition ইনস্টল নেই। install.bat চালিয়ে আবার চেষ্টা করুন।")
            return
        try:
            self._set_status("মাইক্রোফোন প্রস্তুত হচ্ছে…")
            self.root.update_idletasks()
            self.active_language_code = "bn-BD" if self.language_var.get().startswith("বাংলা") else "en-US"
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.75
            self.microphone = sr.Microphone()
            # Brief ambient-noise calibration improves detection in a normal room.
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone, self._audio_callback, phrase_time_limit=7
            )
            self.is_listening = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self._set_status("শুনছি… এখন অন্য অ্যাপে কার্সর রেখে কথা বলুন।", True)
        except Exception as exc:
            self.is_listening = False
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self._set_status("মাইক্রোফোন চালু করা যায়নি।")
            messagebox.showerror("Microphone error", f"মাইক্রোফোন চালু করা যায়নি।\n\n{exc}\n\nWindows Settings → Privacy & security → Microphone থেকে অনুমতি দিন।")

    def _audio_callback(self, recognizer, audio) -> None:
        try:
            # Snapshot set on the UI thread before the listener starts.
            text = recognizer.recognize_google(audio, language=self.active_language_code)
            text = (text or "").strip()
            if text:
                self.recognition_queue.put(text)
        except sr.UnknownValueError:
            self.recognition_queue.put("__UNRECOGNIZED__")
        except sr.RequestError as exc:
            self.recognition_queue.put(f"__REQUEST_ERROR__{exc}")
        except Exception as exc:
            self.recognition_queue.put(f"__ERROR__{exc}")

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self.recognition_queue.get_nowait()
                if item == "__UNRECOGNIZED__":
                    self._set_status("কথা পরিষ্কার বোঝা যায়নি—আরেকবার বলুন।", self.is_listening)
                elif item.startswith("__REQUEST_ERROR__"):
                    detail = item.removeprefix("__REQUEST_ERROR__")
                    self._set_status("ইন্টারনেট/স্পিচ সার্ভিসে সমস্যা হয়েছে।")
                    messagebox.showwarning("Speech service error", f"ভয়েস শনাক্ত করা যায়নি। ইন্টারনেট সংযোগ পরীক্ষা করুন।\n\n{detail}")
                elif item.startswith("__ERROR__"):
                    self._set_status("অডিও প্রসেসিংয়ে সমস্যা হয়েছে।", self.is_listening)
                else:
                    self._append_transcription(item)
        except queue.Empty:
            pass
        self.root.after(150, self._poll_queue)

    def _append_transcription(self, text: str) -> None:
        current = self.text_box.get("1.0", "end-1c")
        prefix = "" if not current or current.endswith((" ", "\n", "\t")) else " "
        self.text_box.insert("end", prefix + text)
        self.text_box.see("end")
        self._set_status(f"শনাক্ত হয়েছে: {text[:90]}", self.is_listening)
        if self.auto_insert_var.get():
            self._paste_to_active(text)

    def _convert_output(self, text: str) -> str:
        mode = self.output_var.get()
        if mode == "Bijoy Classic (ANSI)":
            if to_bijoy is None:
                raise RuntimeError("bijoy-unicode প্যাকেজ ইনস্টল নেই। install.bat চালান।")
            return to_bijoy(text, flavour="classic")
        # Avro and Bijoy Unicode are both standard Unicode output.
        return text

    def _paste_to_active(self, text: str) -> None:
        if pyperclip is None or pyautogui is None:
            self._set_status("পেস্ট লাইব্রেরি ইনস্টল নেই—ক্লিপবোর্ড ফাংশন ব্যবহার করুন।", self.is_listening)
            return
        try:
            converted = self._convert_output(text)
            pyperclip.copy(converted)
            time.sleep(0.12)
            pyautogui.hotkey("ctrl", "v")
        except Exception as exc:
            self._set_status(f"পেস্ট করা যায়নি: {exc}", self.is_listening)

    def stop_recording(self) -> None:
        if self.stop_listening is not None:
            try:
                self.stop_listening(wait_for_stop=False)
            except Exception:
                pass
        self.stop_listening = None
        self.is_listening = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self._set_status("ভয়েস টাইপিং বন্ধ হয়েছে।", False)

    def _get_selected_or_all_text(self) -> str:
        try:
            return self.text_box.get("sel.first", "sel.last")
        except tk.TclError:
            return self.text_box.get("1.0", "end-1c")

    def paste_manual(self) -> None:
        text = self._get_selected_or_all_text().strip()
        if not text:
            messagebox.showinfo("কোনো লেখা নেই", "আগে কিছু কথা বলুন অথবা টেক্সট লিখুন।")
            return
        if self.output_var.get() == "Bijoy Classic (ANSI)":
            if not messagebox.askyesno("Bijoy ANSI সতর্কতা", "এই লেখা SutonnyMJ/Bijoy ANSI সমর্থিত অ্যাপে পেস্ট হবে। সাধারণ Unicode ওয়েবসাইটে এটি সঠিক দেখাবে না। চালিয়ে যাবেন?"):
                return
        self._paste_to_active(text)

    def copy_text(self) -> None:
        if pyperclip is None:
            messagebox.showerror("Clipboard error", "pyperclip ইনস্টল নেই। install.bat চালান।")
            return
        text = self._get_selected_or_all_text().strip()
        if not text:
            return
        try:
            pyperclip.copy(self._convert_output(text))
            self._set_status("ক্লিপবোর্ডে কপি হয়েছে।", self.is_listening)
        except Exception as exc:
            messagebox.showerror("Copy error", str(exc))

    def save_text(self) -> None:
        text = self.text_box.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showinfo("কোনো লেখা নেই", "সংরক্ষণ করার মতো লেখা নেই।")
            return
        default_name = f"VoxBangla_{datetime.now():%Y%m%d_%H%M}.txt"
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_name,
                                            filetypes=[("Text file", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            Path(path).write_text(text, encoding="utf-8")
            self._set_status(f"Unicode TXT সংরক্ষিত: {Path(path).name}", self.is_listening)
        except OSError as exc:
            messagebox.showerror("Save error", str(exc))

    def clear_text(self) -> None:
        if self.text_box.get("1.0", "end-1c").strip() and not messagebox.askyesno("মুছে ফেলবেন?", "সব ট্রান্সক্রিপশন মুছে ফেলবেন?"):
            return
        self.text_box.delete("1.0", "end")

    def close_app(self) -> None:
        self.stop_recording()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = VoxBanglaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
