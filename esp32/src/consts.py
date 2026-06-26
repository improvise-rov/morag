

IMPROVISE_ASCII_ART_STRING: str = """  _                 ____   _____     ___          
 (_)_ __ ___  _ __ |  _ \\ / _ \\ \\   / (_)___  ___ 
 | | '_ ` _ \\| '_ \\| |_) | | | \\ \\ / /| / __|/ _ \\
 | | | | | | | |_) |  _ <| |_| |\\ V / | \\__ \\  __/
 |_|_| |_| |_| .__/|_| \\_\\\\___/  \\_/  |_|___/\\___|
             |_|                                  """



# network
NETWORK_NAME: str = "morag - improvise"
NETWORK_HOSTNAME: str = "morag"
PORT: int = 8090
PACKET_SIZE: int = 1024

# mechanics
BUOYANCY_SERVO_PIN: int = 4
FEEDBACK_PIN: int = 16
FEEDBACK: bool = False

MIN_FEEDBACK_DC = 0.2
MAX_FEEDBACK_DC = 0.8

PWM_FREQUENCY: int = 50
SERVO_MINIMUM_US: int = 500
SERVO_NEUTRAL_US: int = 1500
SERVO_MAXIMUM_US: int = 2500