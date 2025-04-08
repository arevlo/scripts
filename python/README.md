# 🐍 Python Scripts

This directory contains Python scripts that help with productivity, learning, and fun!

## ⏱️ Focus Timer

A colorful, fun terminal-based timer that helps you stay focused with encouraging messages and app usage tracking. Perfect for Pomodoro sessions!

### Features

- 🎨 Colorful terminal interface with progress bar
- 👻 Encouraging messages from a friendly ghost
- 📊 Tracks which applications you're using during your focus session
- 📈 Generates focus reports to help you understand your work patterns
- 🔔 Beeps when your timer is complete
- 💾 Saves your focus history for future reference
- 🌐 Cross-platform compatible (Windows, macOS, Linux)

### Requirements

- Python 3.6+
- Required packages:
  - psutil
  - colorama
  - tzlocal
  - pywin32 (Windows only)
  - pyobjc-framework-AppKit (macOS, optional for window tracking)

### Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install psutil colorama tzlocal
```

For Windows users, also install:
```bash
pip install pywin32
```

For macOS users with full window tracking:
```bash
pip install pyobjc-framework-AppKit
```

### Usage

```bash
# Run a 25-minute focus session
python timer.py 25m

# Run a 1 hour and 30 minute session
python timer.py 1h30m

# Run a 90-second session
python timer.py 90s

# View your focus history
python timer.py --report

# See today's focus stats
python timer.py --today

# View stats for a specific date
python timer.py --date 2023-05-15

# Run without tracking (no data saved)
python timer.py 30m --notrack
```

### Time Formats

The timer accepts various time formats:
- Minutes: `25m`, `1.5m`
- Hours: `1h`, `1.5h`
- Combined: `1h30m`, `1h30m30s`
- Seconds: `90s`

### Focus Reports

The focus report shows:
- Total focus time
- Average focus rating
- Top applications used
- Session breakdown
- Focus patterns and suggestions

### Platform-Specific Notes

- **Windows**: Full application tracking and window detection
- **macOS**: Full functionality with system sounds and application tracking (requires pyobjc-framework-AppKit)
- **Linux**: Basic functionality with terminal bell sound (no window tracking)

### Tips

- Use the timer for Pomodoro sessions (25 minutes work, 5 minutes break)
- Check your focus reports regularly to identify distractions
- Try to minimize app switching for better focus scores
- The ghost's messages are more frequent when time is running low!

---

*Happy focusing! 👻* 