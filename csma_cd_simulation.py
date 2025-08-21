import matplotlib.pyplot as plt
import numpy as np
import random
import time
from matplotlib.widgets import Button  # Import Button for manual control

# Set up figure and axes
fig, ax = plt.subplots(figsize=(12, 6))
plt.title('CSMA/CD Simulation', fontsize=16)
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
status_text = ax.text(5, 10, '', fontsize=12, va='top', ha='left', bbox=dict(facecolor='white', alpha=0.8))

# Medium line
ax.plot([0, 100], [50, 50], 'k--', linewidth=1)

# Globals for animation
lines = []
events = []

# Simulation parameters
devices = list(device_positions.keys())
medium_busy = False
transmitting_devices = []
collision_detected = False
backoff_timers = {}

# Function to reset lines
def clear_lines():
    global lines
    for line in lines:
        line.remove()
    lines = []

# Function to perform sensing
def sense_medium():
    return not medium_busy

# Function to initiate transmission
def transmit(device):
    global lines
    x, y = device_positions[device]
    line, = ax.plot([x, x], [y, 50], color='blue', linewidth=2, linestyle='-')
    lines.append(line)

# Function to show collision
def show_collision(devices_involved):
    global lines
    for device in devices_involved:
        x, y = device_positions[device]
        line, = ax.plot([x, x], [y, 50], color='red', linewidth=3, linestyle='-')
        lines.append(line)

# Function to show successful transmission
def show_success(device):
    global lines
    x, y = device_positions[device]
    line, = ax.plot([x, x], [y, 50], color='green', linewidth=3, linestyle='-')
    lines.append(line)

# Main simulation step
def update(frame):
    global medium_busy, transmitting_devices, collision_detected, backoff_timers

    clear_lines()

    event_log = ''

    # Randomly decide which devices want to transmit
    if not transmitting_devices and not backoff_timers:
        wanting_to_transmit = random.sample(devices, random.randint(1, 4))
        event_log += f"Sensing Medium...\nDevices attempting: {', '.join(wanting_to_transmit)}\n"
        time.sleep(0.5)

        if sense_medium():
            if len(wanting_to_transmit) > 1:
                # Collision occurs
                collision_detected = True
                medium_busy = True
                transmitting_devices = wanting_to_transmit
                show_collision(transmitting_devices)
                event_log += "⚡ Collision Detected!\n"
                # Assign random backoff times
                for device in transmitting_devices:
                    backoff_timers[device] = random.randint(2, 6)
            else:
                # Successful transmission
                device = wanting_to_transmit[0]
                show_success(device)
                medium_busy = True
                transmitting_devices = [device]
                event_log += f"✅ {device} transmitted successfully!\n"

    elif transmitting_devices:
        # Medium becomes free after transmission or collision
        medium_busy = False
        transmitting_devices = []
        event_log += "Medium is now free.\n"

    elif backoff_timers:
        # Handle backoff timers
        event_log += "Backoff Timers:\n"
        to_remove = []
        ready_to_transmit = []
        for device in backoff_timers:
            backoff_timers[device] -= 1
            event_log += f"⏳ {device}: {backoff_timers[device]} sec\n"
            if backoff_timers[device] <= 0:
                ready_to_transmit.append(device)
                to_remove.append(device)
        for device in to_remove:
            del backoff_timers[device]
        # Only allow one device to transmit per step
        if ready_to_transmit:
            device = ready_to_transmit[0]
            if sense_medium():
                show_success(device)
                medium_busy = True
                transmitting_devices = [device]
                event_log += f"✅ {device} transmitted successfully after backoff!\n"
            else:
                # If medium is busy, put device back into backoff for 1 more second
                backoff_timers[device] = 1
                event_log += f"❌ {device} tried to transmit but medium was busy, backing off again.\n"

    # Update the status text
    status_text.set_text(event_log)

# Function for Next Step button
def next_step(event):
    update(None)  # Call the update function manually when the button is clicked
    fig.canvas.draw_idle()  # Redraw the canvas to reflect changes

# Add button for manual control
ax_button = plt.axes([0.45, 0.02, 0.1, 0.05])  # Define button position and size
button = Button(ax_button, 'Next Step', color='lightgoldenrodyellow')
button.on_clicked(next_step)

# Remove automatic animation
# Comment out or remove the following line to stop automatic updates
# ani = animation.FuncAnimation(fig, update, frames=200, interval=1500, repeat=False)

plt.show()
