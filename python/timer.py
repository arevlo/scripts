import time
import os
import psutil
import datetime
import platform
import random
from collections import defaultdict
import json
import re
import sys
import argparse
from datetime import datetime
from colorama import init, Fore, Style

# Platform-specific imports
if platform.system() == "Windows":
    import winsound
    import win32gui
elif platform.system() == "Darwin":  # macOS
    import subprocess
    # Try to import macOS-specific modules, with fallback if not available
    try:
        from AppKit import NSWorkspace
        MACOS_WINDOW_TRACKING = True
    except ImportError:
        MACOS_WINDOW_TRACKING = False
        print("Note: For full macOS window tracking, install PyObjC: pip install pyobjc-framework-AppKit")

# Make sure import is at the top
try:
    import tzlocal
except ImportError:
    print("Installing tzlocal module...")
    os.system('pip install tzlocal')
    import tzlocal

init()

# File to store focus data
FOCUS_DATA_FILE = os.path.join(os.path.expanduser("~"), ".focus_history.json")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def beep():
    if platform.system() == "Windows":
        winsound.Beep(1000, 1000)
    elif platform.system() == "Darwin":  # macOS
        os.system('afplay /System/Library/Sounds/Ping.aiff')
    else:  # Linux and others
        print('\a')  # ASCII bell character

def get_color(seconds_left):
    if seconds_left <= 120:
        return Fore.LIGHTRED_EX
    elif seconds_left <= 300:
        return Fore.LIGHTYELLOW_EX
    return Fore.LIGHTWHITE_EX

def get_funny_ascii(seconds_left):
    # Higher chance of showing a message (30% chance each second)
    if random.random() > 0.30:
        return None
    
    funny_ascii = [
        # Ghost's encouragements and reminders
        "Keep going!",
        "You're doing great!",
        "Stay focused!",
        "Don't give up!",
        "Almost there!",
        "You can do it!",
        "Keep it up!",
        "Making progress!",
        "Stay on task!",
        "Keep working!",
    ]
    
    # Special end-related messages when time is running out
    if seconds_left <= 10:
        last_minute = [
            "Hurry up!!",
            "Time's almost up!",
            "Seconds left!",
            "Finish now!",
            "Final stretch!"
        ]
        funny_ascii.extend(last_minute)
    
    return random.choice(funny_ascii)

def draw_timer(seconds_left, total_seconds, app_tracker):
    mins, secs = divmod(seconds_left, 60)
    time_str = f"{mins:02d}:{secs:02d}"
    bar_length = 40
    fill_ratio = (total_seconds - seconds_left) / total_seconds
    filled = int(bar_length * fill_ratio)
    bar = "█" * filled + " " * (bar_length - filled)
    
    # Color based on time remaining
    bar_color = get_color(seconds_left)
    
    # Get a funny message
    funny = get_funny_ascii(seconds_left)
    
    # Clean, minimal design with added spacing
    print(f"{Fore.LIGHTCYAN_EX}Countdown Timer{Style.RESET_ALL}")
    print()  # Extra spacing
    
    # Progress bar and message side by side
    progress_bar = f"[{bar_color}{bar}{Style.RESET_ALL}]"
    
    if funny:
        ghost_message = f"  👻 {Fore.YELLOW}{funny}{Style.RESET_ALL}"
        print(f"{progress_bar}{ghost_message}")
    else:
        print(progress_bar)
    
    print()  # Extra spacing
    print(f"{Fore.WHITE}Time Left: {time_str}{Style.RESET_ALL}")
    print()  # Extra spacing at the bottom

def track_application(current_app, app_tracker):
    """Track the time spent in different applications"""
    if current_app and len(current_app.strip()) > 0:
        app_name = current_app
        # Simplify app name if it's too long or has a path
        if " - " in app_name:
            app_name = app_name.split(" - ")[-1]
        elif "/" in app_name:
            app_name = app_name.split("/")[-1]
        elif "\\" in app_name:
            app_name = app_name.split("\\")[-1]
            
        # Truncate if still too long
        if len(app_name) > 30:
            app_name = app_name[:27] + "..."
            
        app_tracker[app_name] += 1
    return app_tracker

def get_active_window_macos():
    """Get the active window information on macOS"""
    if not MACOS_WINDOW_TRACKING:
        return "Active Window (macOS)"
    
    try:
        workspace = NSWorkspace.sharedWorkspace()
        active_app = workspace.activeApplication()
        app_name = active_app['NSApplicationName']
        return app_name
    except Exception as e:
        return f"Active Window (macOS) - Error: {str(e)}"

def draw_sysinfo(app_tracker):
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    local_tz = tzlocal.get_localzone()
    now = datetime.now(local_tz).strftime("%I:%M:%S %p %Z")
    top_window = "N/A"
    
    if platform.system() == "Windows":
        try:
            top_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except:
            pass
    elif platform.system() == "Darwin":  # macOS
        top_window = get_active_window_macos()
    
    width = 80
    divider = Fore.LIGHTBLACK_EX + "─" * width + Style.RESET_ALL
    cpu_line = f"{Fore.LIGHTMAGENTA_EX}🧠 CPU:{Style.RESET_ALL} {cpu:.1f}%"
    mem_line = f"{Fore.LIGHTMAGENTA_EX}🧠 RAM:{Style.RESET_ALL} {mem:.1f}%"
    time_line = f"{Fore.LIGHTWHITE_EX}🕓 Time:{Style.RESET_ALL} {now}"
    window_line = f"{Fore.LIGHTCYAN_EX}🔲 Active:{Style.RESET_ALL} {top_window[:50]}"
    
    print(divider)
    print(cpu_line)
    print(mem_line)
    print(time_line)
    print(window_line)
    print(divider)
    
    # Track the current application
    app_tracker = track_application(top_window, app_tracker)
    
    return app_tracker

def save_focus_data(app_tracker, total_seconds, focus_rating, start_time=None):
    """Save the focus session data to a JSON file"""
    if start_time is None:
        start_time = datetime.now().isoformat()
    
    # Prepare data to save
    session_data = {
        "timestamp": start_time,
        "duration_seconds": total_seconds,
        "focus_rating": focus_rating,
        "app_usage": dict(app_tracker)
    }
    
    # Load existing data
    existing_data = []
    if os.path.exists(FOCUS_DATA_FILE):
        try:
            with open(FOCUS_DATA_FILE, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not read focus history file. Starting fresh.")
    
    # Add new session and save
    existing_data.append(session_data)
    
    with open(FOCUS_DATA_FILE, 'w') as f:
        json.dump(existing_data, f, indent=2)
    
    print(f"{Fore.CYAN}Focus session data saved.{Style.RESET_ALL}")

def get_focus_report(date_filter=None):
    """Generate a report of focus sessions"""
    if not os.path.exists(FOCUS_DATA_FILE):
        print(f"{Fore.YELLOW}No focus history found.{Style.RESET_ALL}")
        return
    
    try:
        with open(FOCUS_DATA_FILE, 'r') as f:
            sessions = json.load(f)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error reading focus history file.{Style.RESET_ALL}")
        return
    
    if not sessions:
        print(f"{Fore.YELLOW}No focus sessions recorded yet.{Style.RESET_ALL}")
        return
    
    # Filter sessions by date if requested
    if date_filter:
        filtered_sessions = []
        for session in sessions:
            session_date = datetime.fromisoformat(session["timestamp"]).strftime("%Y-%m-%d")
            if session_date == date_filter:
                filtered_sessions.append(session)
        sessions = filtered_sessions
    
    if not sessions:
        print(f"{Fore.YELLOW}No sessions found for {date_filter}{Style.RESET_ALL}")
        return
    
    # Calculate statistics
    total_focus_time = sum(s["duration_seconds"] for s in sessions)
    avg_focus_rating = sum(s["focus_rating"] for s in sessions) / len(sessions)
    
    # Aggregate app usage across all sessions
    all_apps = defaultdict(int)
    for session in sessions:
        for app, duration in session.get("app_usage", {}).items():
            all_apps[app] += duration
    
    top_apps = sorted(all_apps.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Print report
    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 FOCUS HISTORY REPORT{Style.RESET_ALL}")
    if date_filter:
        print(f"{Fore.CYAN}Date: {date_filter}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    
    # Session summary
    hours, remainder = divmod(total_focus_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_str = f"{hours}h {minutes}m" if hours else f"{minutes}m {seconds}s"
    
    print(f"\n{Fore.WHITE}Total Sessions: {len(sessions)}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Focus Time: {time_str}{Style.RESET_ALL}")
    
    # Focus score
    print(f"{Fore.WHITE}Average Focus Rating: ", end="")
    if avg_focus_rating >= 80:
        print(f"{Fore.LIGHTGREEN_EX}Excellent ({avg_focus_rating:.1f}%){Style.RESET_ALL}")
    elif avg_focus_rating >= 60:
        print(f"{Fore.GREEN}Good ({avg_focus_rating:.1f}%){Style.RESET_ALL}")
    elif avg_focus_rating >= 40:
        print(f"{Fore.YELLOW}Fair ({avg_focus_rating:.1f}%){Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTRED_EX}Needs Improvement ({avg_focus_rating:.1f}%){Style.RESET_ALL}")
    
    # Top applications
    print(f"\n{Fore.CYAN}Top Applications:{Style.RESET_ALL}")
    for app, duration in top_apps:
        minutes = duration / 60
        time_str = f"{minutes:.1f} min" if minutes >= 1 else f"{duration} sec"
        percentage = (duration / sum(t for _, t in all_apps.items())) * 100
        print(f"{Fore.WHITE}{app[:30]:<30} {time_str} ({percentage:.1f}%){Style.RESET_ALL}")
    
    # Session breakdown
    print(f"\n{Fore.CYAN}Session Breakdown:{Style.RESET_ALL}")
    for i, session in enumerate(sorted(sessions, key=lambda s: s["timestamp"])):
        timestamp = datetime.fromisoformat(session["timestamp"])
        duration_min = session["duration_seconds"] / 60
        print(f"{Fore.WHITE}{i+1}. {timestamp.strftime('%H:%M:%S')} - {duration_min:.1f}min - Rating: {session['focus_rating']:.1f}%{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    
    return sessions

def draw_focus_score(app_tracker, total_seconds, save_data=True):
    """Display detailed focus statistics at the end of the session"""
    if not app_tracker:
        print(f"{Fore.YELLOW}No application usage data collected.{Style.RESET_ALL}")
        return 0
    
    print(f"\n{Fore.CYAN}📊 FOCUS SCORE SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}───────────────────────────────────────{Style.RESET_ALL}")
    
    # Get top applications by usage time
    top_apps = sorted(app_tracker.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate percentages
    total_tracked = sum(count for _, count in top_apps)
    if total_tracked == 0:
        print(f"{Fore.YELLOW}No application usage data collected.{Style.RESET_ALL}")
        return 0
    
    # Show top 5 applications or fewer if less were used
    shown_apps = 0
    for i, (app, count) in enumerate(top_apps[:5]):
        if count == 0:
            continue
            
        shown_apps += 1
        percentage = (count / total_tracked) * 100
        bar_length = 30
        filled = int((count / total_tracked) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Determine color based on percentage (more focus = greener)
        if percentage > 80:
            color = Fore.LIGHTGREEN_EX
        elif percentage > 60:
            color = Fore.GREEN
        elif percentage > 40:
            color = Fore.YELLOW
        elif percentage > 20:
            color = Fore.LIGHTYELLOW_EX
        else:
            color = Fore.LIGHTRED_EX
            
        seconds = count
        minutes = seconds / 60
        time_str = f"{minutes:.1f} min" if minutes >= 1 else f"{seconds} sec"
        
        print(f"{color}{app[:25]:<25} [{bar}] {percentage:.1f}% ({time_str}){Style.RESET_ALL}")
    
    if shown_apps == 0:
        print(f"{Fore.YELLOW}No significant application usage detected.{Style.RESET_ALL}")
        return 0
        
    # Overall focus score (fewer app switches = better focus)
    app_switches = len([app for app, count in top_apps if count > 2])  # Count meaningful switches
    focus_rating = 100 - min(80, (app_switches - 1) * 5)  # Penalize for app switching
    
    # Adjust for very short sessions where high switches are normal
    if total_seconds < 300:  # Less than 5 minutes
        focus_rating = min(100, focus_rating + 20)
    
    # Time distribution (how evenly time was spent across apps)
    if len(top_apps) > 1:
        top_app_percentage = (top_apps[0][1] / total_tracked) * 100
        if top_app_percentage > 90:
            distribution = "Excellent focus on primary task"
        elif top_app_percentage > 70:
            distribution = "Good focus with minimal distractions"
        elif top_app_percentage > 50:
            distribution = "Moderate focus with some task switching"
        else:
            distribution = "Frequent context switching"
    else:
        distribution = "Single task focus"
    
    print(f"\n{Fore.CYAN}Session Duration:{Style.RESET_ALL} {total_seconds//60} min {total_seconds%60} sec")
    print(f"{Fore.CYAN}Apps Used:{Style.RESET_ALL} {app_switches}")
    
    print(f"\n{Fore.CYAN}Focus Rating:{Style.RESET_ALL} ", end="")
    
    # Color based on focus rating
    if focus_rating >= 80:
        print(f"{Fore.LIGHTGREEN_EX}Excellent ({focus_rating}%){Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}▰▰▰▰▰{Style.RESET_ALL}")
    elif focus_rating >= 60:
        print(f"{Fore.GREEN}Good ({focus_rating}%){Style.RESET_ALL}")
        print(f"{Fore.GREEN}▰▰▰▰{Fore.LIGHTBLACK_EX}▱{Style.RESET_ALL}")
    elif focus_rating >= 40:
        print(f"{Fore.YELLOW}Fair ({focus_rating}%){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}▰▰▰{Fore.LIGHTBLACK_EX}▱▱{Style.RESET_ALL}")
    elif focus_rating >= 20:
        print(f"{Fore.LIGHTYELLOW_EX}Needs Improvement ({focus_rating}%){Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}▰▰{Fore.LIGHTBLACK_EX}▱▱▱{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTRED_EX}Poor ({focus_rating}%){Style.RESET_ALL}")
        print(f"{Fore.LIGHTRED_EX}▰{Fore.LIGHTBLACK_EX}▱▱▱▱{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}Focus Pattern:{Style.RESET_ALL} {distribution}")
        
    # Suggestion based on focus
    if focus_rating < 50:
        print(f"\n{Fore.LIGHTCYAN_EX}Tip: Try to minimize switching between applications for better focus.{Style.RESET_ALL}")
    elif app_switches > 3:
        print(f"\n{Fore.LIGHTCYAN_EX}Tip: Consider using a pomodoro technique to maintain consistent focus.{Style.RESET_ALL}")
    
    print(f"{Fore.LIGHTBLACK_EX}───────────────────────────────────────{Style.RESET_ALL}")
    
    # Save session data if requested
    if save_data:
        save_focus_data(app_tracker, total_seconds, focus_rating)
    
    return focus_rating

def countdown(seconds, save_data=True, start_time=None):
    """Run the countdown timer and track focus
    
    Args:
        seconds: Duration in seconds
        save_data: Whether to save focus data
        start_time: ISO format timestamp for when the timer started
    """
    total = seconds
    app_tracker = app_tracker = defaultdict(int)
    
    try:
        while seconds >= 0:
            clear()
            draw_timer(seconds, total, app_tracker)
            app_tracker = draw_sysinfo(app_tracker)
            time.sleep(1)
            seconds -= 1
        
        # Time's up - show final screen with focus score
        clear()
        print(f"{Fore.CYAN}⏰ Time's up! DONE!{Style.RESET_ALL}\n")
        
        # Calculate and display focus score
        focus_rating = draw_focus_score(app_tracker, total, save_data=save_data)
        beep()
        return focus_rating
        
    except KeyboardInterrupt:
        clear()
        print(f"{Fore.YELLOW}⏹ Timer canceled.{Style.RESET_ALL}\n")
        # Show focus score for the time that was completed
        focus_rating = draw_focus_score(app_tracker, total - seconds, save_data=save_data)
        return focus_rating

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Focus Timer with tracking')
    parser.add_argument('time', nargs='?', default='2m', 
                      help='Timer duration (e.g., 25m, 1h30m, 90s)')
    parser.add_argument('-r', '--report', action='store_true',
                      help='Show focus history report instead of starting timer')
    parser.add_argument('-d', '--date', type=str,
                      help='Show report for specific date (YYYY-MM-DD)')
    parser.add_argument('-t', '--today', action='store_true',
                      help='Show report for today only')
    parser.add_argument('--notrack', action='store_true',
                      help="Don't save focus data for this session")
    
    args = parser.parse_args()
    
    # Report mode - show focus history
    if args.report or args.date or args.today:
        date_filter = None
        if args.date:
            date_filter = args.date
        elif args.today:
            date_filter = datetime.now().strftime("%Y-%m-%d")
        
        get_focus_report(date_filter)
        sys.exit(0)
    
    # Timer mode - parse time and start countdown
    time_arg = args.time.lower()
    duration = 120  # Default: 2 minutes
    
    # Parse time argument
    if time_arg.isdigit():  # Plain number is treated as minutes
        duration = int(time_arg) * 60
    else:
        # Try to parse formats like "1h30m", "45m", "1.5h", etc.
        hours = re.search(r'(\d+\.?\d*)h', time_arg)
        minutes = re.search(r'(\d+\.?\d*)m', time_arg)
        seconds = re.search(r'(\d+\.?\d*)s', time_arg)
        
        total_seconds = 0
        if hours:
            total_seconds += float(hours.group(1)) * 3600
        if minutes:
            total_seconds += float(minutes.group(1)) * 60
        if seconds:
            total_seconds += float(seconds.group(1))
            
        if total_seconds > 0:
            duration = int(total_seconds)
        else:
            print(f"Couldn't understand time format: {time_arg}")
            print("Examples: 30m, 1h, 1h30m, 90s")
            print("Using default time of 2 minutes.")
    
    # Display info about the timer's duration
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 and hours == 0:  # Only show seconds if less than an hour
        time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")
    
    time_str = " and ".join(time_parts)
    print(f"{Fore.CYAN}Starting timer for {time_str}{Style.RESET_ALL}")
    if args.notrack:
        print(f"{Fore.YELLOW}Note: This session will not be saved to focus history.{Style.RESET_ALL}")
    time.sleep(1.5)  # Brief pause to show the duration
    
    # Record start time
    start_time = datetime.now().isoformat()
    
    # Start the countdown
    result = countdown(duration, save_data=(not args.notrack), start_time=start_time)