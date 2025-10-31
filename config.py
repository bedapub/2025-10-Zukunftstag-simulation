"""
Configuration constants for the Zukunftstag simulation application.
"""

# Development mode (set to False for production)
DEV_MODE = True

# Development/Test settings
DEV_BYPASS_QR = True  # Allow registration without QR code in dev mode
DEV_AUTO_LOGIN_TEAM = "Herceptin"  # Auto-select this team in dev mode (set to None to disable)
DEV_GENERATE_TEST_DATA = True  # Auto-generate test data on startup

# Admin authentication
ADMIN_PASSWORD = "admin123"

# Session types
SESSION_OPTIONS = {
    "morning": "Morning Session (09:00 - 11:30)",
    "afternoon": "Afternoon Session (13:30 - 16:00)",
    "test": "Test Session"
}

# Game constants
PERIMETER_GROUND_TRUTH = 28.0  # meters
MEMORY_GAME_TOTAL_ROUNDS = 5

# Validation constraints
HEIGHT_MIN = 50  # cm
HEIGHT_MAX = 250  # cm
PERIMETER_MIN = 5  # meters
PERIMETER_MAX = 100  # meters
NAME_MIN_LENGTH = 2

# Pain score scale for clinical trial
PAIN_SCORE_MIN = 0
PAIN_SCORE_MAX = 10

# Color Palette - Roche Brand Colors
# Primary Blues
COLOR_PRIMARY_BLUE = '#0b41cd'
COLOR_DARK_BLUE = '#022366'
COLOR_BRIGHT_BLUE = '#1482fa'
COLOR_LIGHT_BLUE = '#bde3ff'

# Warm Neutrals
COLOR_PEACH_1 = '#fac9b5'
COLOR_PEACH_2 = '#fad6c7'
COLOR_PEACH_3 = '#ffe8de'
COLOR_PEACH_4 = '#fff7f5'

# Cool Neutrals
COLOR_GRAY_1 = '#544f4f'
COLOR_GRAY_2 = '#706b69'
COLOR_GRAY_3 = '#c2bab5'
COLOR_GRAY_4 = '#dbd6d1'
COLOR_GRAY_5 = '#f5f5f2'

# Reds
COLOR_RED_1 = '#8c0000'
COLOR_RED_2 = '#c40000'
COLOR_RED_3 = '#ff1f26'
COLOR_RED_4 = '#ff8782'

# Oranges
COLOR_ORANGE_1 = '#b22b0d'
COLOR_ORANGE_2 = '#ed4a0d'
COLOR_ORANGE_3 = '#ff7d29'
COLOR_ORANGE_4 = '#ffbd69'

# Purples
COLOR_PURPLE_1 = '#7d0096'
COLOR_PURPLE_2 = '#bc36f0'
COLOR_PURPLE_3 = '#e085fc'
COLOR_PURPLE_4 = '#f2d4ff'

# Application-specific color assignments
COLOR_PARENT = COLOR_ORANGE_2  # Parent data - Roche orange
COLOR_CHILD = COLOR_PEACH_3    # Child data - light warm tone
COLOR_PLACEBO = COLOR_LIGHT_BLUE  # Placebo - light blue
COLOR_MEDICINE = COLOR_PURPLE_4   # Medicine - light purple
COLOR_SUCCESS = COLOR_BRIGHT_BLUE # Success states
COLOR_WARNING = COLOR_ORANGE_3    # Warnings
COLOR_ERROR = COLOR_RED_3         # Errors
COLOR_PRIMARY = COLOR_PRIMARY_BLUE  # Primary brand color

# Chart colors for visualizations
CHART_COLORS = [
    COLOR_PRIMARY_BLUE,
    COLOR_ORANGE_2,
    COLOR_PURPLE_2,
    COLOR_BRIGHT_BLUE,
    COLOR_RED_2,
    COLOR_ORANGE_3,
    COLOR_PURPLE_3,
    COLOR_DARK_BLUE
]

# Medals for winners
MEDALS = ["🥇", "🥈", "🥉"]

# Database random seed (for consistent simulations)
RANDOM_SEED = 1887

# File paths
DATA_DIR = "data"
TEAM_NAMES_FILE = f"{DATA_DIR}/team_namen.txt"
CHILD_NAMES_FILE = f"{DATA_DIR}/kinder_vornamen.txt"
PARENT_NAMES_FILE = f"{DATA_DIR}/eltern_vornamen.txt"
