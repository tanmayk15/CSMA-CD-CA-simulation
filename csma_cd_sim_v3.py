import matplotlib.pyplot as plt
import random
from matplotlib.widgets import Button
import matplotlib.animation as animation

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
status_text = ax.text(
    5, 10, '', fontsize=11, va='top', ha='left',
    bbox=dict(facecolor='white', alpha=0.85, boxstyle='round,pad=0.5', edgecolor='gray'),
    wrap=True
)

# Medium line
ax.plot([0, 100], [50, 50], 'k--', linewidth=1)

# Globals
lines = []
devices = list(device_positions.keys())
medium_busy = False
transmitting_devices = []
backoff_timers = {}
collision_detected = False
auto_running = False  # Whether auto simulation is running
manual_step = False   # Whether a manual next step is requested

# Clear all drawn lines
def clear_lines():
    global lines
    for line in lines:
        line.remove()
    lines = []

# Sense medium
def sense_medium():
    return not medium_busy

# Show transmission
def show_transmission(device, color='green'):
    global lines
    x, y = device_positions[device]
    line, = ax.plot([x, x], [y, 50], color=color, linewidth=3)
    lines.append(line)

# Show collision
def show_collision(devices_involved):
    for device in devices_involved:
        show_transmission(device, color='red')

# Main simulation logic (do one step)
def simulation_step():
    global medium_busy, transmitting_devices, backoff_timers, collision_detected

    clear_lines()
    event_log = ''

    if not transmitting_devices and not backoff_timers:
        wanting_to_transmit = random.sample(devices, random.randint(1, 4))
        event_log += f"Sensing Medium...\nDevices attempting: {', '.join(wanting_to_transmit)}\n"

        if sense_medium():
            if len(wanting_to_transmit) > 1:
                collision_detected = True
                medium_busy = True
                transmitting_devices = wanting_to_transmit
                show_collision(transmitting_devices)
                event_log += "⚡ Collision Detected!\n"

                # Assign backoff timers
                for device in transmitting_devices:
                    backoff_timers[device] = random.randint(2, 6)
            else:
                device = wanting_to_transmit[0]
                show_transmission(device, color='green')
                medium_busy = True
                transmitting_devices = [device]
                event_log += f"✅ {device} transmitted successfully!\n"

    elif transmitting_devices:
        medium_busy = False
        transmitting_devices = []
        event_log += "Medium is now free.\n"

    elif backoff_timers:
        event_log += "Backoff Timers:\n"
        ready_to_transmit = []

        # Display backoff timers
        for device in backoff_timers:
            event_log += f"⏳ {device}: {backoff_timers[device]} sec\n"

        # Check for duplicate timers (collision on backoff)
        backoff_values = list(backoff_timers.values())
        duplicate_times = [t for t in set(backoff_values) if backoff_values.count(t) > 1 and t > 0]

        if duplicate_times:
            event_log += "⚡ Collision again due to same backoff! Applying Binary Exponential Backoff...\n"
            devices_with_duplicates = [device for device in backoff_timers if backoff_timers[device] in duplicate_times]
            for device in devices_with_duplicates:
                backoff_timers[device] = random.randint(2, 12)
        else:
            for device in list(backoff_timers.keys()):
                if backoff_timers[device] == 0:
                    ready_to_transmit.append(device)
                else:
                    backoff_timers[device] -= 1

            for device in ready_to_transmit:
                if sense_medium():
                    show_transmission(device, color='green')
                    medium_busy = True
                    transmitting_devices = [device]
                    event_log += f"✅ {device} transmitted successfully after backoff!\n"
                    del backoff_timers[device]
                    break
                else:
                    backoff_timers[device] = 1
                    event_log += f"❌ {device} tried but medium busy. Backing off again.\n"

    status_text.set_text(event_log)
    fig.canvas.draw_idle()

# --- Button Handlers ---

# Next Step button
def next_step(event):
    global manual_step
    manual_step = True

# Auto Simulate button
def auto_simulate(event):
    global auto_running
    auto_running = not auto_running
    auto_button.label.set_text('Pause' if auto_running else 'Auto Simulate')

# Exit button
def exit_program(event):
    plt.close(fig)

# --- Animation Handler ---
def animate(frame):
    global manual_step

    if auto_running or manual_step:
        simulation_step()
        manual_step = False  # reset manual step

# --- Add Buttons ---

# Next Step button
ax_next = plt.axes([0.82, 0.02, 0.13, 0.06])
next_button = Button(ax_next, 'Next Step', color='lightblue', hovercolor='deepskyblue')
next_button.on_clicked(next_step)

# Auto Simulate button
ax_auto = plt.axes([0.82, 0.09, 0.13, 0.06])
auto_button = Button(ax_auto, 'Auto Simulate', color='lightgreen', hovercolor='lime')
auto_button.on_clicked(auto_simulate)

# Exit button
ax_exit = plt.axes([0.82, 0.16, 0.13, 0.06])
exit_button = Button(ax_exit, 'Exit', color='salmon', hovercolor='red')
exit_button.on_clicked(exit_program)

# --- Animation ---
ani = animation.FuncAnimation(fig, animate, interval=800)

# --- Show ---
plt.show()
