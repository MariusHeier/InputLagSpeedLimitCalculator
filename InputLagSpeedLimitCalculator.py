import os
import sys
from kivy.resources import resource_add_path, resource_find
import random
import socket
import struct
import select
from datetime import datetime
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.core.window import Window
from kivy.core.text import LabelBase, FontContextManager as FCM
from kivy.core.audio import SoundLoader
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label


# Add the root path of the PyInstaller bundle to Kivy's resource paths
if hasattr(sys, '_MEIPASS'):
    resource_add_path(os.path.join(sys._MEIPASS))

# Resources
sound_file = resource_find('ItIsAGoodDay.mp3')
image_file = resource_find('hoodie_figure_big.png')
font_file = resource_find('VT323-Regular.ttf')

dark_background = (0.08, 0.08, 0.08, 1)
bright_cyan = (0, 0.8, 0.8, 1)
text_color = (0.85, 0.85, 0.85, 1)
bright_yellow = (1, 0.95, 0, 1)

def game(selected_data, num_rounds=10, extra_lag_amount=0):
    player1_wins, player2_wins = 0, 0
    len_data = len(selected_data)

    # Random start indices for both players
    player1_start = random.randint(0, len_data - 1)
    player2_start = random.randint(0, len_data - 1)

    for round_num in range(num_rounds):
        player1_index = (player1_start + round_num) % len_data
        player2_index = (player2_start - round_num - 2) % len_data  # Adjusting for Python's negative indexing

        player1_choice = selected_data[player1_index]
        player2_choice = selected_data[player2_index] + extra_lag_amount

        if player1_choice < player2_choice:
            player1_wins += 1
        else:
            player2_wins += 1

    return player1_wins, player2_wins

def multi_game(selected_data, num_rounds=10, multi_game_count=100, lag_resolution=0.01, max_lag=10, window_size=100, primary_target=0.90, secondary_target=0.80):
    win_rates = []
    extra_lag_values = []
    extra_lag_amount = 0
    primary_target_achieved = False

    while extra_lag_amount <= max_lag:
        player1_wins, player2_wins = 0, 0
        for _ in range(multi_game_count):
            game_result = game(selected_data, num_rounds, extra_lag_amount)
            player1_wins += game_result[0]
            player2_wins += game_result[1]

        current_win_rate = player1_wins / (player1_wins + player2_wins) if player2_wins + player1_wins > 0 else 0
        win_rates.append(current_win_rate)
        extra_lag_values.append(extra_lag_amount)

        if current_win_rate >= primary_target:
            primary_target_achieved = True
            break  # Stop if the primary target is achieved

        if len(win_rates) >= window_size:
            # Check if the secondary target win rate is stable over the window
            window_avg = sum(win_rates[-window_size:]) / window_size
            if primary_target_achieved or window_avg >= secondary_target:
                break  # Stop if the secondary target is stable or already achieved primary target

        extra_lag_amount += lag_resolution

    return extra_lag_values, win_rates, primary_target_achieved
# Function to calculate the checksum of the input bytes
def checksum(source_string):
    sum = 0
    max_count = (len(source_string) // 2) * 2
    count = 0
    while count < max_count:
        val = source_string[count + 1]*256 + source_string[count]
        sum = sum + val
        sum = sum & 0xffffffff
        count = count + 2

    if max_count < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# Function to create a new echo request packet
def create_packet(id, size=59):
    header = struct.pack("bbHHh", 8, 0, 0, id, 1)
    data = size * "Q"
    my_checksum = checksum(header + data.encode('utf-8'))
    header = struct.pack("bbHHh", 8, 0, socket.htons(my_checksum), id, 1)
    return header + data.encode('utf-8')

# Function to send a single ping
def ping(host):
    icmp = socket.getprotobyname("icmp")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("ll", 2, 0))  # Timeout of 2 seconds
    except socket.error as e:
        if e.errno == 1:
            e.msg += " - Note that ICMP messages can only be sent from processes running as root."
            raise socket.error(e.msg)
        return None
    except Exception as e:
        print("Exception: " + str(e))
        return None

    my_id = datetime.now().microsecond & 0xFFFF
    packet = create_packet(my_id)
    sent_time = datetime.now()
    sock.sendto(packet, (host, 1))
    
    while True:
        ready = select.select([sock], [], [], 2)
        if ready[0] == []:
            return None  # If timeout occurs, return None

        time_received = datetime.now()
        rec_packet, addr = sock.recvfrom(1024)
        icmp_header = rec_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
        if packet_id == my_id:
            return (sent_time, time_received)
# Custom Spinner styling
class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super(CustomSpinnerOption, self).__init__(**kwargs)
        self.background_color = (0, 0.24, 0.35, 1)  # dark_background
        self.color = (0, 0.8, 0.8, 1)  # bright_cyan
        self.font_name = 'VT323-Regular.ttf'
        self.size_hint_y = None
        self.height = 30
        self.font_size = 16

class RetroApp(App):
    def on_region_change(self, spinner, text):
        # Clear the collected data
        self.ping_data.clear()
        self.data_label.text = "Data cleared, waiting for new ping results..."

    def build(self):
        # Threshold for win rate stability (adjust as needed)
        self.title = 'InputLagSpeedLimitCalculator.exe'
        self.target_win_rate = 90  # Adjust as needed
        Window.size = (450, 450)
        # Ensure font is registered using the correct path
        LabelBase.register(name='RetroFont', fn_regular=font_file)
        #LabelBase.register(name='RetroFont', fn_regular='VT323-Regular.ttf')

        self.regions = {
            "NA-East": "ping-nae.ds.on.epicgames.com",
            "NA-Central": "ping-nac.ds.on.epicgames.com",
            "NA-West": "ping-naw.ds.on.epicgames.com",
            "Europe": "ping-eu.ds.on.epicgames.com",
            "Oceania": "ping-oce.ds.on.epicgames.com",
            "Brazil": "ping-br.ds.on.epicgames.com",
            "Asia": "ping-asia.ds.on.epicgames.com"
        }

        float_layout = FloatLayout()
        bg_img = Image(source=image_file, allow_stretch=True, keep_ratio=False)
        float_layout.add_widget(bg_img)
        logo_label = Label(text="InputLagSpeedLimitCalculator.exe", font_name='RetroFont', font_size=20, color=bright_cyan, size_hint=(None, None), size=(400, 50), pos_hint={'center_x': 0.5, 'top': 1})
        float_layout.add_widget(logo_label)

        author_label = Label(text="by mariusheier on youtube", font_name='RetroFont', font_size=12, color=bright_cyan, size_hint=(None, None), size=(400, 30), pos_hint={'center_x': 0.5, 'top': 0.95})
        float_layout.add_widget(author_label)

        self.spinner = Spinner(
            text='Select Server',
            values=('NA-East', 'NA-Central', 'NA-West', 'Europe', 'Oceania', 'Brazil', 'Asia'),
            size_hint=(0.8, None),
            height=30,
            font_name='RetroFont',
            color=bright_cyan,
            font_size=16,
            pos_hint={'center_x': 0.5, 'top': 0.1},
            background_color=(0, 0.24, 0.35, 1),
            option_cls=CustomSpinnerOption
        )
        self.spinner.bind(text=self.on_region_change)
        float_layout.add_widget(self.spinner)

        # Data display label
        self.data_label = Label(text="", font_name='RetroFont', font_size=20, color=bright_cyan, size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5, 'center_y': 0.14})
        float_layout.add_widget(self.data_label)

        # Label for "Input lag speed limit:" text
        self.simulation_text_label = Label(text="Input lag speed limit @ win rate:", font_name='RetroFont', font_size=20, color=bright_cyan, size_hint=(None, None), size=(400, 30), pos_hint={'center_x': 0.5, 'center_y': 0.27})
        float_layout.add_widget(self.simulation_text_label)

        # Label for displaying the numbers
        self.simulation_data_label = Label(text="-", font_name='RetroFont', font_size=30, color=bright_yellow, size_hint=(None, None), size=(400, 50), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        float_layout.add_widget(self.simulation_data_label)

        # Initialize data collection
        self.ping_data = []
        self.window_size = 500  # Adjustable as needed

        # Scheduling data updates
        Clock.schedule_interval(self.update_data, 0.01)

        return float_layout

    def update_data(self, dt):
        selected_region = self.spinner.text
        host = self.regions.get(selected_region)
        if host:
            result = ping(host)
            if result:
                sent_time, received_time = result
                ping_duration = (received_time - sent_time).total_seconds() * 1000
                self.data_label.text = f"Ping: {ping_duration:.2f} ms"

                # Collect ping data for game simulation
                self.ping_data.append(ping_duration)

                # Update label to show the progress of data collection
                data_collected = len(self.ping_data)
                if data_collected < self.window_size:
                    self.simulation_data_label.text = f"Data collected: {data_collected} / {self.window_size}"
                else:
                    # Start the simulation if enough data points are collected
                    extra_lag_values, win_rates, primary_target_achieved = multi_game(
                        self.ping_data[-self.window_size:],
                        num_rounds=10,
                        multi_game_count=100,
                        lag_resolution=0.1,
                        max_lag=30,
                        window_size=self.window_size,
                        primary_target=0.90,
                        secondary_target=0.80
                    )

                    # Determine if primary or secondary target is achieved
                    final_win_rate = win_rates[-1]
                    if primary_target_achieved:
                        status_text = f"{extra_lag_values[-1]:.1f} ms @ 90%"
                    elif final_win_rate >= 0.80:
                        status_text = f"{extra_lag_values[-1]:.1f} ms @ 80%"
                    else:
                        status_text = "Target not reached"

                    self.simulation_data_label.text = status_text
            else:
                self.data_label.text = "Ping failed"
        else:
            self.data_label.text = "Region not selected"

    def on_start(self):
        # Load sound using the resource_find result
        self.sound = SoundLoader.load(sound_file)
        if self.sound:
            self.sound.loop = True
            self.sound.play()
   
    
if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    RetroApp().run()