import pygame
import sys
import threading
import sounddevice as sd
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import pygame
import time
import os
pygame.init()

current_screen = "menu"
selected_instrument = None
is_busy = False
status_message = "Waiting for command..."

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice Band Simulator")

ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin", "ffmpeg.exe")
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
AudioSegment.converter = which("ffmpeg")

if getattr(sys, '_MEIPASS', False):
    base_dir = sys._MEIPASS  
else:
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

asset_dir = os.path.join(base_dir, "assets")
instruments_dir = os.path.join(base_dir, "instruments")
final_dir = os.path.join(base_dir, "final")
sounds_dir = os.path.join(base_dir, "sounds")

background_file = os.path.join(asset_dir, "background.jpg")
background_image = pygame.image.load(background_file)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 22)

class Button:
    """Custom button for GUI with shadow and hover effects."""
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (10, 40, 100)
        self.text_color = (255, 255, 255)
        self.border_color = (255, 255, 255)
        self.shadow_offset = 4
        self.radius = 12

    def draw(self):
        """Draw button with shadow and label."""
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=self.radius)

        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.radius)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=self.radius)

        label = small_font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        """Execute action if button is clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                threading.Thread(target=self.action).start()

def reset_mixer():
    """Stops and re-initializes the mixer safely."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        time.sleep(0.3)  
    pygame.mixer.init()
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])

def ensure_dirs():
    os.makedirs(instruments_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

def fade_audio(audio):
    return audio.fade_in(2000).fade_out(2000)

def cut_or_loop(audio, duration):
    if len(audio) > duration:
        return audio[:duration]
    else:
        loops = duration // len(audio)
        remainder = duration % len(audio)
        return (audio * loops) + audio[:remainder]

def recognize_speech(prompt="Speak now..."):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        
        set_status(prompt)
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    return recognizer.recognize_google(audio)

def set_status(msg):
    global status_message
    status_message = msg

def record_vocals(filename= os.path.join(instruments_dir, "vocals_loop.wav"), duration=30):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        
        
        set_status("Recording vocals...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.record(source, duration=duration)
    if os.path.exists(filename):
        os.chmod(filename, 0o666)

    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    time.sleep(0.5)  
    with open(filename, "wb") as f:
        f.write(audio.get_wav_data())
    
    
    set_status("Saved vocals: " + filename)
    return filename


def process_notes(instrument, notes):
    ensure_dirs()
    files = []
    pygame.mixer.music.stop()
    for note in notes:
        note_file = os.path.join(sounds_dir, instrument, f"{note}.wav")
        if os.path.exists(note_file):
            files.append(AudioSegment.from_file(note_file))
        else:
            
            set_status(f"Warning: {note_file} not found.")
            
            files.append(AudioSegment.silent(duration=500))
    combined = sum(files, AudioSegment.empty())
    output_file = os.path.join(instruments_dir, f"{instrument}_loop.wav")
    if os.path.exists(output_file):
        os.remove(output_file)
    combined.export(output_file, format='wav')
    set_status(f"Saved {instrument} loop: {output_file}")
    


def select_instrument(inst):
    global selected_instrument, current_screen
    selected_instrument = inst
    current_screen = inst
    set_status(f"Selected {inst}")
    

def make_song_cmd():
    global status_message
    status_message = "Mixing song..."
    pygame.mixer.music.stop()
    
    create_final_song()
    status_message = "Song mixed!"

def play_song_cmd():
    global status_message
    status_message = "Playing final song..."
    file = os.path.join(final_dir, "final_song.wav")
    

    if os.path.exists(file):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    else:
        status_message = "Final song not found."
    
        
def threaded_voice_command(prompt, context):
    global is_busy, status_message
    global current_screen 
    is_busy = True
    status_message = "Listening..."
    try:
        command = recognize_speech(prompt).lower()
        
        status_message = "Heard: " + command
        if "select" in command:
            for inst in ["piano", "guitar", "drum", "vocals", "flute"]:
                if inst in command:
                    select_instrument(inst)
                    break
        elif "make song" in command:
            make_song_cmd()
        elif "play song" in command:
            play_song_cmd()
        elif "pause song" in command:
            pause_final_song()
        elif "record" in command:
            if context == "vocals":
                # Directly record 30-second vocal track
                record_vocals()
                status_message = "Vocals recorded successfully!"
            else:
                # Instrument: activate and record notes by voice
                record_instrument_loop(context)
                status_message = f"{context} loop recorded successfully!"
        elif "play" in command:
                play_instr_cmd(current_screen)
        elif "pause" in command:
            pause_instrument()
        elif "back" in command:
            current_screen = "menu"
        else:
            status_message = "Command not recognized."
    except Exception as e:
        

        status_message = "Error with voice input."
    finally:
        is_busy = False

def set_menu():
    """Switch back to main menu."""
    global current_screen, status_message
    current_screen = "menu"
    status_message = "Waiting for command..."

def record_vocal_cmd():
    """Record vocals directly."""
    global is_busy, status_message
    if is_busy:
        return
    is_busy = True
    status_message = "Recording vocals..."
    pygame.mixer.music.stop()
    record_vocals()
    is_busy = False
    status_message = "Vocals recorded successfully!"

def record_instrument_loop(instr):
    """Listen to spoken note sequence and generate 30-second instrument loop."""
    
    recognizer = sr.Recognizer()
    notes = []
    reset_mixer()
    global status_message
    
    status_message="Say the sounds for {instr} (e.g., '0 or 1 or 2 or 3')"
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        
        status_message = "Listening for note name ..."
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio)
        
        status_message = f"Recording {instr} loop..."
        words = spoken_text.lower().replace('-', ' ').replace(',', ' ').split()
        word_to_digit = {
            "zero": "0", "one": "1", "two": "2", "three": "3",
            "four": "4", "five": "5", "six": "6", "seven": "7",
            "eight": "8", "nine": "9"
        }

        for word in words:
            if word in word_to_digit:
                notes.append(word_to_digit[word])
            elif word.isdigit():
                
                notes.extend(list(word))
            else:
                
                status_message = f"Ignored word: {word}"

        if not notes:
            
            status_message = "No valid notes detected."
            return

        
        note_segments = []
        for note in notes:
            note_path = os.path.join(sounds_dir, instr, f"{note}.wav")
            if os.path.exists(note_path):
                note_segments.append(AudioSegment.from_file(note_path))
            else:
                
                status_message = f"Warning: {note_path} not found."
                note_segments.append(AudioSegment.silent(duration=500))

     
        loop = sum(note_segments, AudioSegment.empty())
        final_loop = cut_or_loop(loop, 30_000)
        final_loop = fade_audio(final_loop)

        output_path = os.path.join(instruments_dir, f"{instr}_loop.wav")
        final_loop.export(output_path, format="wav")
        
        status_message = f"{instr} loop recorded successfully!"

    except Exception as e:
        
        status_message = "Error with voice input."

def create_final_song(output_file=os.path.join(final_dir, "final_song.wav"), duration_ms=30_000):
    """Mix all instrument loops and optional vocals into one final song."""
    ensure_dirs()
    global status_message
    
    vocals_file = os.path.join(instruments_dir, "vocals_loop.wav")

    pygame.mixer.music.stop()
    final_mix = AudioSegment.silent(duration=duration_ms)
   
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    time.sleep(0.5)
    pygame.mixer.init()

    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except PermissionError:
            
            status_message = f"File {output_file} is currently in use. Make sure it's not being played."
            return

    for filename in os.listdir(instruments_dir):
        if filename.endswith(".wav"):
            filepath = os.path.join(instruments_dir, filename)
            try:
                audio = AudioSegment.from_file(filepath)
                audio = audio - 6
                processed = fade_audio(cut_or_loop(audio, duration_ms))
                final_mix = final_mix.overlay(processed)
            except Exception as e:
                
                status_message=f"Error loading {filepath}: {e}"

    if os.path.exists(vocals_file):
        vocals = AudioSegment.from_file(vocals_file)
        vocals = vocals + 12
        aligned_vocals = fade_audio(cut_or_loop(vocals, duration_ms))
        final_mix = final_mix.overlay(aligned_vocals)

    final_mix.export(output_file, format="wav")
    
    status_message = "Final song created successfully!"    
    return output_file


def pause_song_cmd():
    """Pause final song."""
    global status_message
    status_message = "Pausing final song..."
    pause_final_song()
    status_message = "Paused"


def play_instr_cmd(instr):
    """Play a single instrument's loop."""
    global status_message
    status_message = f"Playing {instr} loop..."
    play_instrument(instr)
    status_message = "Done"


def pause_instr_cmd(instr):
    """Pause a single instrument's loop."""
    global status_message
    status_message = f"Pausing {instr} loop..."
    pause_instrument()
    status_message = "Paused"

def play_file(filename):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1) 

def pause_playback():
    """Pause currently playing audio."""
    pygame.mixer.music.pause()
    pygame.mixer.music.stop()

def play_instrument(instr):
    """Play the previously recorded loop for this instrument."""
    global status_message
    filename = os.path.join(instruments_dir, f"{instr}_loop.wav")

    if os.path.exists(filename):
        play_file(filename)
    else:       
        status_message=f"Instrument file {filename} not found."

def pause_instrument():
    """Pause currently playing instrument loop."""
    pause_playback()
    pygame.mixer.music.stop()


def pause_final_song():
    """Pause the final song."""
    pause_playback()
    pygame.mixer.music.stop()


def play_final_song(filename):
    """Play back the final song."""
    play_file(filename)
    pygame.mixer.music.stop()

def cut_or_loop(audio, duration_ms=30_000):
    """Repeat or cut audio to exactly `duration_ms` milliseconds."""
    if len(audio) >= duration_ms:
        return audio[:duration_ms]
    else:
        
        times = (duration_ms // len(audio)) + 1
        looped = AudioSegment.empty()
        for i in range(times):
            looped += audio
        return looped[:duration_ms]
    
def fade_audio(audio, fade_duration_ms=2000):
    """Add fade in and fade out to audio."""
    return audio.fade_in(fade_duration_ms).fade_out(fade_duration_ms)

def align_vocal_to_instrument(vocal, instrument):
    """Make sure vocal is the same length as the instrument by looping or cutting."""
    if len(vocal) < len(instrument):
       
        return cut_or_loop(vocal, len(instrument))
    else:
        
        return vocal[:len(instrument)]


def create_menu_buttons():
    """Create main menu button set."""
    button_width, button_height = 200, 50
    padding = 20
    col_gap = 60
    total_columns = 2
    
    instruments = ["piano", "drum", "guitar", "vocals", "flute"]
    actions = [(f"Select {inst.capitalize()}", lambda inst=inst: select_instrument(inst)) for inst in instruments]
    actions += [("Make Final Song", make_song_cmd),
                ("Play Final Song", play_song_cmd),
                ("Pause Final Song", pause_song_cmd)]

    total = len(actions)
    num_rows = (total + 1) // 2
    total_height = num_rows * button_height + (num_rows - 1) * padding
    start_y = (HEIGHT - total_height) // 2

    total_width = total_columns * button_width + (total_columns - 1) * col_gap
    start_x = (WIDTH - total_width) // 2

    buttons = []

    for i, (label, action) in enumerate(actions):
        col = i % 2
        row = i // 2
        x = start_x + col * (button_width + col_gap)
        y = start_y + row * (button_height + padding)
        button = Button(x, y, button_width, button_height, label, action)
        buttons.append(button)

    return buttons

def create_instrument_buttons():
    """Create button set for instrument view."""
    button_width, button_height = 200, 50
    center_x = WIDTH // 2 - button_width // 2
    def record_action():
        if selected_instrument == "vocals":
            record_vocals()  
        else:
            record_instrument_loop(selected_instrument)
    return [
        Button(center_x, 280, button_width, button_height, "Record", record_action),
        Button(center_x, 350, button_width, button_height, "Play Loop", lambda: play_instr_cmd(selected_instrument)),
        Button(center_x, 420, button_width, button_height, "Pause Loop", lambda: pause_instr_cmd(selected_instrument)),
        Button(center_x, 490, button_width, button_height, "Back", set_menu),
    ]



def main():
    """Main GUI Loop with voice and button control."""
    global is_busy, current_screen, status_message
    
    clock = pygame.time.Clock()
    menu_buttons = create_menu_buttons()

    instrument_backgrounds = {
    "piano": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "piano.png")),
        (WIDTH, HEIGHT)
    ),
    "drum": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "drum.png")),
        (WIDTH, HEIGHT)
    ),
    "guitar": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "guitar.png")),
        (WIDTH, HEIGHT)
    ),
    "vocals": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "mic.png")),
        (WIDTH, HEIGHT)
    ),
    "flute": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "flute.png")),
        (WIDTH, HEIGHT)
    )
}
    voice_timer = pygame.time.get_ticks()

    running = True
    while running:
        clock.tick(30)
        screen.blit(background_image, (0, 0))

        if current_screen == "menu":
            for button in menu_buttons:
                button.draw()
        else:
            bg = instrument_backgrounds.get(current_screen)
            if bg:
                screen.blit(bg, (0, 0))
            title = font.render(f"{current_screen.capitalize()} Instrument", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

            for button in create_instrument_buttons():
                button.draw()

        status = font.render(status_message, True, (255, 255, 0))
        screen.blit(status, (50, HEIGHT - 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if current_screen == "menu":
                for button in menu_buttons:
                    button.handle_event(event)
            else:
                for button in create_instrument_buttons():
                    button.handle_event(event)
        
        now = pygame.time.get_ticks()
        if not is_busy and now - voice_timer > 5000:
            prompt = ("Say a command like 'select piano/guitar/vocals', 'make song', 'play song', or 'pause song'" 
                      if current_screen == "menu" 
                      else "Say 'play', 'pause', 'record', or 'back'")
            threaded_thread = threading.Thread(target=threaded_voice_command, args=(prompt, current_screen))
            threaded_thread.start()
            voice_timer = now

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
