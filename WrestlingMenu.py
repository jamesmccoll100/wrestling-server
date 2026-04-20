import curses
import subprocess
import pygame
import os
import json

def get_bret_progress_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), ".bret_progress.json")

def load_bret_high_scores():
    path = get_bret_progress_path()
    if not os.path.exists(path):
        return {"wins": 0, "losses": 0, "draws": 0}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            # Ensure we have the required keys
            if "wins" not in data:
                data["wins"] = 0
            if "losses" not in data:
                data["losses"] = 0
            if "draws" not in data:
                data["draws"] = 0
            return data
    except Exception:
        return {"wins": 0, "losses": 0, "draws": 0}

def display_match_record(stdscr):
    stats = load_bret_high_scores()

    current_row = 0
    color_flash = True

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Stats
        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        draws = stats.get("draws", 0)
        total_matches = wins + losses + draws
        win_percentage = (wins / total_matches * 100) if total_matches > 0 else 0

        # Box dimensions
        box_width = 60
        box_height = 20
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2

        # Border with exception handling
        stdscr.attron(curses.color_pair(16))
        for i in range(box_height):
            for j in range(box_width):
                if i == 0 or i == box_height - 1:
                    try:
                        stdscr.addch(box_y + i, box_x + j, curses.ACS_HLINE)
                    except curses.error:
                        pass
                elif j == 0 or j == box_width - 1:
                    try:
                        stdscr.addch(box_y + i, box_x + j, curses.ACS_VLINE)
                    except curses.error:
                        pass
                else:
                    try:
                        stdscr.addch(box_y + i, box_x + j, ' ')
                    except curses.error:
                        pass
        # Corners with exception handling
        try:
            stdscr.addch(box_y, box_x, curses.ACS_ULCORNER)
            stdscr.addch(box_y, box_x + box_width - 1, curses.ACS_URCORNER)
            stdscr.addch(box_y + box_height - 1, box_x, curses.ACS_LLCORNER)
            stdscr.addch(box_y + box_height - 1, box_x + box_width - 1, curses.ACS_LRCORNER)
        except curses.error:
            pass
        stdscr.attroff(curses.color_pair(16))

        # Title
        title = " MATCH RECORD "
        try:
            stdscr.addstr(
                box_y,
                box_x + box_width // 2 - len(title) // 2,
                title,
                curses.color_pair(16)
            )
        except curses.error:
            pass

        # Total matches + win rate
        total_text = f"Total Matches: {total_matches}"
        try:
            stdscr.addstr(box_y + 2, box_x + box_width // 2 - len(total_text) // 2, total_text, curses.color_pair(1))
        except curses.error:
            pass

        if total_matches > 0:
            percent_text = f"Win Rate: {win_percentage:.1f}%"
            try:
                stdscr.addstr(box_y + 3, box_x + box_width // 2 - len(percent_text) // 2, percent_text, curses.color_pair(1))
            except curses.error:
                pass

        # Separator
        sep_y = box_y + 4
        for j in range(1, box_width - 1):
            try:
                stdscr.addch(sep_y, box_x + j, curses.ACS_HLINE)
            except curses.error:
                pass

        # Columns
        col_y = sep_y + 2
        col_width = 18

        # Wins
        try:
            stdscr.addstr(col_y, box_x + 6 + col_width // 2 - 2, "WINS", curses.color_pair(20))
            stdscr.addstr(col_y + 2, box_x + 6 + col_width // 2, str(wins), curses.color_pair(20))
        except curses.error:
            pass

        # Losses
        mid_x = box_x + box_width // 2 - col_width // 2
        try:
            stdscr.addstr(col_y, mid_x + col_width // 2 - 4, "LOSSES", curses.color_pair(21))
            stdscr.addstr(col_y + 2, mid_x + col_width // 2, str(losses), curses.color_pair(21))
        except curses.error:
            pass

        # Draws
        right_x = box_x + box_width - col_width - 6
        try:
            stdscr.addstr(col_y, right_x + col_width // 2 - 3, "DRAWS", curses.color_pair(22))
            stdscr.addstr(col_y + 2, right_x + col_width // 2, str(draws), curses.color_pair(22))
        except curses.error:
            pass

        # Vertical separators
        for i in range(col_y, col_y + 5):
            try:
                stdscr.addch(i, box_x + 24, curses.ACS_VLINE)
                stdscr.addch(i, box_x + 36, curses.ACS_VLINE)
            except curses.error:
                pass

        # Exit option
        option = "Back to Main Menu"
        opt_x = box_x + box_width // 2 - len(option) // 2
        opt_y = box_y + box_height - 3

        try:
            if color_flash:
                stdscr.attron(curses.color_pair(5))
                stdscr.addstr(opt_y, opt_x, option)
                stdscr.attroff(curses.color_pair(5))
            else:
                stdscr.attron(curses.color_pair(9))
                stdscr.addstr(opt_y, opt_x, option)
                stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        stdscr.refresh()
        color_flash = not color_flash

        key = stdscr.getch()
        if key in [27, curses.KEY_ENTER, 10, 13]:
            return

GREEN = '\033[32m'  
MAGENTA = '\033[95m'
CYAN = '\033[94m'
YELLOW = '\033[33m'  
RESET = '\033[0m'

def check_screen_size(stdscr, mode="menu"):
    """Check if screen is large enough for content"""
    h, w = stdscr.getmaxyx()
    
    if mode == "menu":
        min_width = 70
        min_height = 20
        message = "screen to small to display the menu"
    else:  # stats
        min_width = 36
        min_height = 20
        message = "screen to small to display stats"
    
    if w < min_width or h < min_height:
        stdscr.clear()
        x = max(0, w // 2 - len(message) // 2)
        y = max(0, h // 2)
        try:
            stdscr.addstr(y, x, message, curses.color_pair(1))
            stdscr.refresh()
        except curses.error:
            pass  # Screen is too small even for error message
        return False
    return True

def print_large_title(stdscr):
    if not check_screen_size(stdscr, "menu"):
        return
    
    title = [
        "██╗    ██╗██████╗ ███████╗███████╗████████╗██╗     ██╗███╗   ██╗ ██████╗",
        "██║    ██║██╔══██╗██╔════╝██╔════╝╚══██╔══╝██║     ██║████╗  ██║██╔════╝",
        "██║ █╗ ██║██████╔╝█████╗  ███████╗   ██║   ██║     ██║██╔██╗ ██║██║  ███╗",
        "██║███╗██║██╔══██╗██╔══╝  ╚════██║   ██║   ██║     ██║██║╚██╗██║██║   ██║",
        "╚███╔███╔╝██║  ██║███████╗███████║   ██║   ███████╗██║██║ ╚████║╚██████╔╝",
        " ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ",
        "                                                                         ",
        " █████╗ ██████╗ ███████╗███╗   ██╗ █████╗ ",
        "██╔══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗",
        "███████║██████╔╝█████╗  ██╔██╗ ██║███████║",
        "██╔══██║██╔══██╗██╔══╝  ██║╚██╗██║██╔══██║",
        "██║  ██║██║  ██║███████╗██║ ╚████║██║  ██║",
        "╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝"
    ]

    subtitle = "The Best There Ever Will Be"

    h, w = stdscr.getmaxyx()
    
    # Display subtitle
    subtitle_x = w // 2 - len(subtitle) // 2
    subtitle_y = 1
    try:
        stdscr.addstr(subtitle_y, subtitle_x, subtitle, curses.color_pair(16))
    except curses.error:
        pass
    
    # Adjust title position to be below the subtitle
    title_start_y = subtitle_y + 2

    for idx, line in enumerate(title):
        x = w // 2 - len(line) // 2
        y = title_start_y + idx
        try:
            stdscr.addstr(y, x, line, curses.color_pair(16))
        except curses.error:
            pass

def print_menu(stdscr, selected_row_idx, color_flash, wins=0, tag_color_pair=None):
    stdscr.clear()
    
    if not check_screen_size(stdscr, "menu"):
        return

    h, w = stdscr.getmaxyx()
    
    # Create menu based on wins - with simpler formatting
    menu = ["Challanger", "Match Record"]
    if wins >= 5:
        menu.append("Tag-Team Match")  # No asterisks in the actual menu text
    menu.append("Exit")
    
    total_items = len(menu)
    tag_team_unlocked = wins >= 5

    print_large_title(stdscr)

    # Add the "Select Challenger" text above the menu options
    select_text = "-Select Mode-"
    select_text_x = w // 2 - len(select_text) // 2
    select_text_y = h // 2 - total_items // 2 + 4
    try:
        stdscr.addstr(select_text_y, select_text_x, select_text, curses.color_pair(1))
    except curses.error:
        pass

    for idx, row in enumerate(menu):
        x = w // 2 - len(row) // 2
        y = h // 2 - total_items // 2 + idx + 6

        try:
            if idx == selected_row_idx:
                # Draw highlight background for selected item
                highlight_color = curses.color_pair(5) if color_flash else curses.color_pair(9)
                stdscr.attron(highlight_color)
                
                if row == "Tag-Team Match" and tag_color_pair:
                    # For Tag-Team Match with asterisk decorations
                    display_text = f"* {row} *"
                    display_x = w // 2 - len(display_text) // 2
                    
                    # Draw left asterisk with rotating color
                    stdscr.attroff(highlight_color)
                    stdscr.attron(curses.color_pair(tag_color_pair))
                    stdscr.addch(y, display_x, '*')
                    stdscr.attroff(curses.color_pair(tag_color_pair))
                    
                    # Draw space without highlight, then text with highlight
                    stdscr.addch(y, display_x + 1, ' ')  # Space without highlight
                    stdscr.attron(highlight_color)
                    stdscr.addstr(y, display_x + 2, row)  # Text with highlight
                    stdscr.attroff(highlight_color)
                    stdscr.addch(y, display_x + 2 + len(row), ' ')  # Space without highlight
                    
                    # Draw right asterisk with rotating color
                    stdscr.attron(curses.color_pair(tag_color_pair))
                    stdscr.addch(y, display_x + len(display_text) - 1, '*')
                    stdscr.attroff(curses.color_pair(tag_color_pair))
                else:
                    # Normal selected item
                    stdscr.addstr(y, x, row)
                stdscr.attroff(highlight_color)
            else:
                # Not selected
                if row == "Tag-Team Match" and tag_color_pair:
                    # For Tag-Team Match with asterisk decorations
                    display_text = f"* {row} *"
                    display_x = w // 2 - len(display_text) // 2
                    
                    # Draw left asterisk with rotating color
                    stdscr.attron(curses.color_pair(tag_color_pair))
                    stdscr.addch(y, display_x, '*')
                    stdscr.attroff(curses.color_pair(tag_color_pair))
                    
                    # Draw space
                    stdscr.addch(y, display_x + 1, ' ')
                    
                    # Draw text with normal color
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(y, display_x + 2, row)
                    stdscr.attroff(curses.color_pair(4))
                    
                    # Draw space
                    stdscr.addch(y, display_x + 2 + len(row), ' ')
                    
                    # Draw right asterisk with rotating color
                    stdscr.attron(curses.color_pair(tag_color_pair))
                    stdscr.addch(y, display_x + 2 + len(row) + 1, '*')
                    stdscr.attroff(curses.color_pair(tag_color_pair))
                else:
                    # Normal unselected item
                    if row == "Challanger":
                        stdscr.attron(curses.color_pair(1))
                    elif row == "Match Record":
                        stdscr.attron(curses.color_pair(3))
                    elif row == "Exit":
                        stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(y, x, row)
                    if row in ["Challanger", "Match Record", "Exit"]:
                        stdscr.attroff(curses.color_pair(1) if row == "Challanger" or row == "Exit" else curses.color_pair(3))
        except curses.error:
            pass

    # Add multi-line footer text to the bottom right corner
    footer_lines = [
        "© JAMES MCCOLL. INC",
        "NORTH WEST. UK. 2026"
    ]
    
    footer_x = w - max(len(line) for line in footer_lines) - 1
    footer_y_start = h - len(footer_lines) - 1

    for i, line in enumerate(footer_lines):
        try:
            stdscr.addstr(footer_y_start + i, footer_x, line, curses.color_pair(1))
        except curses.error:
            pass

    stdscr.refresh()
    
    footer_x = w - max(len(line) for line in footer_lines) - 1
    footer_y_start = h - len(footer_lines) - 1

    for i, line in enumerate(footer_lines):
        try:
            stdscr.addstr(footer_y_start + i, footer_x, line, curses.color_pair(1))
        except curses.error:
            pass

    stdscr.refresh()

def display_loading_message(stdscr, message, color_pair):
    h, w = stdscr.getmaxyx()
    for i in range(3):
        stdscr.clear()
        stdscr.bkgd(' ', color_pair)
        x = w // 2 - len(message) // 2
        y = h // 2
        try:
            stdscr.addstr(y, x, message + '.' * (i + 1))
        except curses.error:
            pass
        stdscr.refresh()
        curses.napms(500)

def reset_background(stdscr):
    stdscr.bkgd(' ', curses.color_pair(0))
    stdscr.clear()
    stdscr.refresh()

def start_bret_hart_game(stdscr):
    display_loading_message(stdscr, "Loading game", curses.color_pair(13))
    curses.endwin()
    subprocess.call(["python3", "WrestlingArena.py"])
    reset_background(stdscr)

def start_tag_team_game(stdscr):
    display_loading_message(stdscr, "Loading game", curses.color_pair(15))
    curses.endwin()
    subprocess.call(["python3", "WrestlingArena3.py"])
    reset_background(stdscr)

# ASCII art representations for menu options
ascii_art = {
    "Bret Hart": [
        " ██████╗ ██████╗ ███████╗████████╗",
        " ██╔══██╗██╔══██╗██╔════╝╚══██╔══╝",
        " ██████╔╝██████╔╝█████╗     ██║   ",
        " ██╔══██╗██╔══██╗██╔══╝     ██║   ",
        " ██████╔╝██║  ██║███████╗   ██║   ",
        " ╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ",
        "                                  ",
        " ██╗  ██╗ █████╗ ██████╗ ████████╗",
        " ██║  ██║██╔══██╗██╔══██╗╚══██╔══╝",
        " ███████║███████║██████╔╝   ██║   ",
        " ██╔══██║██╔══██║██╔══██╗   ██║   ",
        " ██║  ██║██║  ██║██║  ██║   ██║   ",
        " ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   "
    ],
}

def print_ascii_art(stdscr, art_lines, art_color, box_x, box_y):
    h, w = stdscr.getmaxyx()
    art_start_x = box_x + 40 + 2
    art_start_y = box_y

    for idx, line in enumerate(art_lines):
        if art_start_y + idx >= h:
            break
        x = art_start_x
        if x + len(line) >= w:
            break
        try:
            stdscr.addstr(art_start_y + idx, x, line, art_color)
        except curses.error:
            pass

animation_frames = ["|", "/", "-", "\\"]

def display_stats_page(stdscr, wrestler):
    stats = {
        "Bret Hart": """Nickname: The Hitman
Height: 6'0"
Weight: 235lbs
Special Move: Sharpshooter
Wrestling Profile:
Pound for pound, Bret Hart is one
of the best wrestlers to ever lace up
his boots. One of Hart's favorite
weapons is the Sharpshooter, which he
delivers with pinpoint accuracy."""
    }

    bret_color = curses.color_pair(17)
    white_color = curses.color_pair(1)

    current_row = 0
    color_flash = True
    frame_count = 0

    while True:
        stdscr.clear()
        
        if not check_screen_size(stdscr, "stats"):
            key = stdscr.getch()
            if key == 27:
                return False
            continue

        h, w = stdscr.getmaxyx()

        box_width = 42
        box_height = 14
        art_lines = ascii_art[wrestler]
        max_line_length = max(len(line) for line in art_lines)
        total_width_needed = box_width + max_line_length + 2
        total_height_needed = max(box_height, len(art_lines))

        box_x = (w - total_width_needed) // 2
        box_y = (h - total_height_needed) // 2

        if wrestler == "Bret Hart":
            box_color_pair = bret_color

        stdscr.attron(box_color_pair)
        for i in range(box_height):
            for j in range(box_width):
                if i == 0 or i == box_height - 1:
                    try:
                        stdscr.addch(box_y + i, box_x + j, curses.ACS_HLINE)
                    except curses.error:
                        pass
                elif j == 0 or j == box_width - 1:
                    try:
                        stdscr.addch(box_y + i, box_x + j, curses.ACS_VLINE)
                    except curses.error:
                        pass
                else:
                    try:
                        stdscr.addch(box_y + i, box_x + j, ' ')
                    except curses.error:
                        pass

        try:
            stdscr.addch(box_y, box_x, curses.ACS_ULCORNER)
            stdscr.addch(box_y, box_x + box_width - 1, curses.ACS_URCORNER)
            stdscr.addch(box_y + box_height - 1, box_x, curses.ACS_LLCORNER)
            stdscr.addch(box_y + box_height - 1, box_x + box_width - 1, curses.ACS_LRCORNER)
        except curses.error:
            pass
        stdscr.attroff(box_color_pair)

        title = f" Challanger stats {animation_frames[frame_count % len(animation_frames)]}"
        title_x = w // 2 - len(title) // 2
        try:
            stdscr.addstr(box_y + 1, box_x + 1, title, curses.color_pair(16))
        except curses.error:
            pass

        lines = stats[wrestler].split('\n')
        for idx, line in enumerate(lines):
            x = box_x + 2
            y = box_y + 3 + idx
            parts = line.split(':', 1)
            if len(parts) == 2:
                label, text = parts
                try:
                    stdscr.addstr(y, x, label + ":", white_color)
                    stdscr.addstr(y, x + len(label) + 1, text, box_color_pair)
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(y, x, line, box_color_pair)
                except curses.error:
                    pass

        if wrestler == "Bret Hart":
            art_color = bret_color

        print_ascii_art(stdscr, art_lines, art_color, box_x, box_y)

        menu = ["Continue", "Back to Main Menu"]
        menu_start_y = box_y + box_height + 1
        color_pairs = {
            0: (curses.color_pair(1), curses.color_pair(5) if color_flash else curses.color_pair(9)),
            1: (curses.color_pair(2), curses.color_pair(6) if color_flash else curses.color_pair(10)),
        }

        for idx, row in enumerate(menu):
            x = w // 2 - len(row) // 2
            y = menu_start_y + idx

            try:
                if idx == current_row:
                    stdscr.attron(color_pairs[idx][1])
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(color_pairs[idx][1])
                else:
                    stdscr.attron(color_pairs[idx][0])
                    stdscr.addstr(y, x, row)
                    stdscr.attroff(color_pairs[idx][0])
            except curses.error:
                pass

        stdscr.refresh()

        key = stdscr.getch()
        color_flash = not color_flash
        frame_count += 1

        if key == curses.KEY_DOWN:
            current_row = (current_row + 1) % 2
        elif key == curses.KEY_UP:
            current_row = (current_row - 1) % 2
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row == 0
        elif key == 27:
            return False

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.timeout(200)

    # Initialize color rotation variables
    color_frame = 0
    tag_colors = [30, 31, 32, 33]
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(16, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(17, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(18, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(19, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(20, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(21, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(22, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(30, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(31, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(32, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(33, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    current_row = 0
    color_flash = True
    
    while True:
        # Load current wins to determine menu options
        stats = load_bret_high_scores()
        wins = stats.get("wins", 0)
        
        # Update color rotation every 10 frames (slower rotation)
        color_frame += 1
        tag_color_index = (color_frame // 3) % len(tag_colors)
        
        print_menu(
            stdscr,
            current_row,
            color_flash,
            wins,
            tag_colors[tag_color_index] if wins >= 5 else None
        )

        key = stdscr.getch()
        color_flash = not color_flash

        # Determine menu items based on wins
        if wins >= 5:
            # Menu with Tag-Team Match: [Challanger, Match Record, Tag-Team, Exit]
            menu_items = 4
            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % menu_items
            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % menu_items
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_row == 0:  # Challanger
                    if display_stats_page(stdscr, "Bret Hart"):
                        start_bret_hart_game(stdscr)
                elif current_row == 1:  # Match Record
                    display_match_record(stdscr)
                elif current_row == 2:  # Tag-Team Match - NO STATS PAGE
                    # Go straight to loading screen and game
                    start_tag_team_game(stdscr)
                elif current_row == 3:  # Exit
                    break
        else:
            # Menu without Tag-Team Match: [Challanger, Match Record, Exit]
            menu_items = 3
            if key == curses.KEY_DOWN:
                current_row = (current_row + 1) % menu_items
            elif key == curses.KEY_UP:
                current_row = (current_row - 1) % menu_items
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_row == 0:  # Challanger
                    if display_stats_page(stdscr, "Bret Hart"):
                        start_bret_hart_game(stdscr)
                elif current_row == 1:  # Match Record
                    display_match_record(stdscr)
                elif current_row == 2:  # Exit
                    break

    curses.endwin()

if __name__ == "__main__":
    # Set terminal size to 90x30
    os.system('printf "\e[8;30;90t"')
    curses.wrapper(main)
