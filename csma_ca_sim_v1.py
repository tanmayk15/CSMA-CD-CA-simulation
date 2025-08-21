import matplotlib.pyplot as plt
import numpy as np
import random
import time
from matplotlib.widgets import Button
import threading
import sys

# Set up figure and axes
fig, ax = plt.subplots(figsize=(12, 6))
plt.title('CSMA/CA Simulation', fontsize=16)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Device positions
device_positions = {
    'Device 1': (10, 80),
    'Device 2': (25, 80),
    'Device 3': (40, 80),
    'Device 4': (55, 80),
    'Device 5': (70, 80),
    'Device 6': (85, 80),
}

# Draw devices
for name, (x, y) in device_positions.items():
    ax.text(x, y + 5, name, ha='center', fontsize=10, fontweight='bold')
    ax.plot(x, y, marker='o', markersize=12, color='black')

# Status box
status_text = ax.text(
    5, 15, '', fontsize=11, va='top', ha='left',
    bbox=dict(facecolor='white', alpha=0.85, boxstyle='round,pad=0.5', edgecolor='gray'),
    wrap=True
)

# Medium line
ax.plot([0, 100], [50, 50], 'k--', linewidth=1)

# Globals
lines = []
medium_busy = False
backoff_timers = {}
waiting_devices = []
current_transmitting_device = None
collision_message = ''
auto_running = [False]  # Mutable flag for Auto Simulate control

# Clear transmission lines
def clear_lines():
    global lines
    for line in lines:
        line.remove()
    lines = []

# Sense medium (True if free)
def sense_medium():
    return not medium_busy

# Show transmission
def show_transmission(device):
    global lines
    x, y = device_positions[device]
    line, = ax.plot([x, x], [y, 50], color='green', linewidth=3, linestyle='-')
    lines.append(line)

# Handle collisions using Binary Exponential Backoff
def handle_collision(backoff_timers):
    global collision_message
    backoff_values = list(backoff_timers.values())
    duplicates = [k for k, v in zip(backoff_timers.keys(), backoff_values) if backoff_values.count(v) > 1]

    if duplicates:
        collision_message = "Collision detected due to same backoff time! Applying Binary Exponential Backoff."
        for device in duplicates:
            backoff_timers[device] = random.randint(2, 6) * 2  # Double the backoff
        return True
    return False

# Main simulation logic
def update(frame):
    global medium_busy, backoff_timers, waiting_devices, current_transmitting_device, collision_message

    clear_lines()
    event_log = ''

    # Finish transmission if a device was transmitting
    if current_transmitting_device:
        event_log += f"✅ {current_transmitting_device} finished transmission.\n"
        medium_busy = False
        current_transmitting_device = None

        if waiting_devices or backoff_timers:
            event_log += "Medium is now free. Devices are still waiting to transmit or have backoff timers.\n"
        else:
            event_log += "Medium is now free. No devices waiting.\n"

    # If no device is transmitting and no device waiting, randomly select devices
    elif not current_transmitting_device and not waiting_devices and not backoff_timers:
        waiting_devices.extend(random.sample(list(device_positions.keys()), random.randint(1, 4)))
        event_log += f"Sensing Medium...\nDevices attempting: {', '.join(waiting_devices)}\n"
        time.sleep(0.5)

        if sense_medium():
            for device in waiting_devices:
                backoff_timers[device] = random.randint(2, 5)
            event_log += "Medium free. Devices start backoff timers.\n\n"

            # Display backoff timers
            event_log += "Backoff Timers Assigned:\n"
            for device in waiting_devices:
                event_log += f"⏳ {device}: {backoff_timers[device]} sec\n"

            if handle_collision(backoff_timers):
                event_log += f"\n{collision_message}\n"
        else:
            event_log += "Medium busy. Devices waiting...\n"

    # If devices are in backoff
    elif backoff_timers:
        event_log += "Backoff Timers:\n"
        ready_to_transmit = []

        for device in list(backoff_timers.keys()):
            if sense_medium():
                backoff_timers[device] -= 1
                event_log += f"⏳ {device}: {backoff_timers[device]} sec\n"

                if backoff_timers[device] <= 0:
                    ready_to_transmit.append(device)
            else:
                event_log += f"⏸️ {device}: Medium busy, pausing backoff at {backoff_timers[device]} sec\n"

        if ready_to_transmit:
            device = ready_to_transmit[0]
            current_transmitting_device = device
            waiting_devices.remove(device)
            del backoff_timers[device]
            show_transmission(device)
            medium_busy = True
            event_log += f"✅ {device} is transmitting now!\n"

    collision_message = ''  # Reset collision message
    status_text.set_text(event_log)

# --- Button Functions ---

# Next Step button function
def next_step(event):
    update(None)
    fig.canvas.draw_idle()

# Auto Simulate button function
def auto_simulate(event):
    if auto_running[0]:
        auto_running[0] = False
        auto_button.label.set_text('Auto Simulate')
        return
    auto_running[0] = True
    auto_button.label.set_text('Pause')

    def auto_loop():
        global medium_busy, backoff_timers, waiting_devices, current_transmitting_device, collision_message
        while auto_running[0]:
            update(None)
            fig.canvas.draw_idle()
            plt.pause(0.8)

            # If simulation cycle finishes, reset and start a new one
            if not current_transmitting_device and not waiting_devices and not backoff_timers:
                status_text.set_text("🔄 New Simulation Starting...\n")
                fig.canvas.draw_idle()
                time.sleep(1)
                clear_lines()
                medium_busy = False
                backoff_timers = {}
                waiting_devices = []
                current_transmitting_device = None
                collision_message = ''

    threading.Thread(target=auto_loop, daemon=True).start()

# Exit button function
def exit_program(event):
    plt.close('all')
    sys.exit()

# --- Adding Buttons to the Plot ---

# Next Step button
ax_button = plt.axes([0.82, 0.02, 0.13, 0.06])
button = Button(ax_button, 'Next Step', color='lightblue', hovercolor='deepskyblue')
button.on_clicked(next_step)

# Auto Simulate button
ax_auto = plt.axes([0.82, 0.09, 0.13, 0.06])
auto_button = Button(ax_auto, 'Auto Simulate', color='lightgreen', hovercolor='lime')
auto_button.on_clicked(auto_simulate)

# Exit button
ax_exit = plt.axes([0.82, 0.16, 0.13, 0.06])
exit_button = Button(ax_exit, 'Exit', color='salmon', hovercolor='red')
exit_button.on_clicked(exit_program)

# --- Show plot ---
plt.show()
