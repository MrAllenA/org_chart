# from parser import parse_custom_markdown
# from render import create_visualization
# markdown_text = """
# # Department: Engineering
# ## Designation: Senior Engineer
# - Role: Lead Projects
# - Role: Mentor Junior Engineers

# ## Designation: Junior Engineer
# - Role: Assist in Projects
# - Role: Learn and Develop Skills

# # Department: HR
# ## Designation: HR Manager
# - Role: Manage Recruitment
# - Role: Oversee Employee Relations
# - Child: Junior Engineer
# """

# parsed_data = parse_custom_markdown(markdown_text)
# print(parsed_data)
# dot = create_visualization(parsed_data)
# dot.render('organization_structure', format='png', view=True)

import pygame
import numpy as np
import pyaudio
import random
from scipy.signal import find_peaks

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 120  # Increased frame rate for smoother animation
BAR_WIDTH = 10
NUM_BARS = 50
CIRCLE_RADIUS = 100
CIRCLE_MARGIN = 20  # Margin between the circle and the bars
MAX_BAR_HEIGHT = HEIGHT - CIRCLE_RADIUS - CIRCLE_MARGIN - 20
BACKGROUND_COLOR = (0, 0, 0)
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
BEAT_THRESHOLD = 0.6  # Adjust this threshold based on the music
PULSE_AMPLITUDE = 30  # Amplitude of the pulse effect
PULSE_FREQUENCY = 0.5  # Frequency of the pulse effect
ROTATE_SPEED = 0.02  # Speed of rotation
RIPPLE_COUNT = 8  # Number of ripple layers for more detailed effect
RIPPLE_MAX_RADIUS = 200  # Maximum radius for the ripples
RIPPLE_GROWTH_RATE = 2.0  # Rate at which ripples grow (increased for more spacing)
RIPPLE_SPEED = 2.0  # Speed of ripple propagation
RIPPLE_OPACITY = 100  # Maximum opacity of the ripples
TEXT_COLOR = (255, 255, 255)  # White color for the text
FONT_SIZE = 40  # Size of the font
STAR_SIZE = 3  # Size of the stars
STAR_COUNT = 30  # Number of stars to show on beat
STAR_POP_DURATION = 500  # Duration for star popping effect in milliseconds
STAR_VELOCITY = 300  # Velocity at which stars shoot out (pixels per second)

# Define a set of pleasant colors
PLEASANT_COLORS = [
    (255, 105, 180),  # Hot Pink
    (255, 165, 0),    # Orange
    (0, 191, 255),    # Deep Sky Blue
    (60, 179, 113),   # Medium Sea Green
    (255, 20, 147),   # Deep Pink
    (255, 215, 0),    # Gold
    (32, 178, 170),   # Light Sea Green
    (255, 69, 0)      # Red-Orange
]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Music Visualizer')
clock = pygame.time.Clock()

# Initialize font
font = pygame.font.Font(None, FONT_SIZE)

# PyAudio setup
p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

# Star class to handle star properties and animations
class Star:
    def __init__(self, x, y, color, angle, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.size = STAR_SIZE
        self.alpha = 255
        self.velocity = velocity
        self.angle = angle
        self.creation_time = pygame.time.get_ticks()
    
    def update(self, current_time, dt):
        elapsed_time = current_time - self.creation_time
        if elapsed_time < STAR_POP_DURATION:
            # Update position based on velocity and direction
            self.x += self.velocity * np.cos(self.angle) * dt
            self.y += self.velocity * np.sin(self.angle) * dt
            # Fade out effect
            factor = (STAR_POP_DURATION - elapsed_time) / STAR_POP_DURATION
            self.size = STAR_SIZE * factor
            self.alpha = 255 * factor
        else:
            self.size = 0
            self.alpha = 0
    
    def draw(self, surface):
        if self.size > 0:
            color_with_alpha = self.color + (int(self.alpha),)
            pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y)), int(self.size))

# Function to draw tiny stars around the circle that shoot out during beats
def draw_stars(stars):
    current_time = pygame.time.get_ticks()
    dt = clock.get_time() / 1000.0  # Time since last frame in seconds
    for star in stars:
        star.update(current_time, dt)
        star.draw(screen)
    # Remove stars that have faded out
    return [star for star in stars if star.alpha > 0]

def get_bar_heights(data):
    # Compute FFT
    fft_data = np.fft.fft(data)
    fft_data = np.abs(fft_data[:len(fft_data) // 2])  # Take only positive frequencies
    
    # Normalize fft_data
    fft_data = fft_data / np.max(fft_data)  # Normalize to [0, 1]
    
    # Interpolate to match the number of bars
    # Use log scale to better match human hearing (optional)
    fft_data = np.log1p(fft_data)  # Apply log transformation for better scaling
    bar_heights = np.interp(np.linspace(0, len(fft_data), NUM_BARS), np.arange(len(fft_data)), fft_data)
    
    # Scale heights to fit the screen
    bar_heights = bar_heights * MAX_BAR_HEIGHT
    
    return bar_heights

def detect_beats(data):
    # Calculate the amplitude envelope
    amplitude_envelope = np.abs(data)
    avg_volume = np.mean(amplitude_envelope)
    
    # Find peaks in the amplitude envelope
    peaks, _ = find_peaks(amplitude_envelope, height=BEAT_THRESHOLD)
    
    # Simple beat detection based on peak count
    return len(peaks) > 0, avg_volume

def color_morph(time):
    """ Return a pleasant color that morphs over time """
    # Use sinusoidal functions to smoothly cycle through pleasant colors
    num_colors = len(PLEASANT_COLORS)
    index1 = int(time % num_colors)
    index2 = (index1 + 1) % num_colors
    fraction = (time % 1)  # Fractional part for smooth transition
    color1 = PLEASANT_COLORS[index1]
    color2 = PLEASANT_COLORS[index2]
    
    r = int(color1[0] * (1 - fraction) + color2[0] * fraction)
    g = int(color1[1] * (1 - fraction) + color2[1] * fraction)
    b = int(color1[2] * (1 - fraction) + color2[2] * fraction)
    
    return (r, g, b)

def rotate_point(x, y, angle):
    """ Rotate point (x, y) by angle radians """
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    return x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle

def draw_ripples(surface, center, time):
    """ Draw colorful ripple effect around the center """
    base_radius = CIRCLE_RADIUS + 20  # Start radius for the outer ripples
    
    # Calculate ripple size factor based on a sinusoidal function for smooth growing and shrinking
    ripple_size_factor = np.sin(RIPPLE_SPEED * time) * 0.5 + 0.5
    
    for i in range(RIPPLE_COUNT):
        ripple_radius = base_radius + i * RIPPLE_GROWTH_RATE * ripple_size_factor
        ripple_color = PLEASANT_COLORS[i % len(PLEASANT_COLORS)]  # Use pleasant colors for each ripple
        ripple_opacity = max(0, RIPPLE_OPACITY * (1 - (ripple_radius / (base_radius + RIPPLE_COUNT * RIPPLE_GROWTH_RATE * ripple_size_factor))))
        ripple_color_with_opacity = ripple_color + (int(ripple_opacity),)
        pygame.draw.circle(surface, ripple_color_with_opacity, center, int(ripple_radius), 1)

def draw_visualizer(bar_heights, beat_detected, stars):
    # Draw background
    screen.fill(BACKGROUND_COLOR)
    
    # Get the current time
    time = pygame.time.get_ticks() / 1000
    
    # Draw the ripples (background effect)
    draw_ripples(screen, (CENTER_X, CENTER_Y), time)
    
    # Draw the central circle with pulsating, rotating effect and color morphing
    pulse_radius = CIRCLE_RADIUS + PULSE_AMPLITUDE * np.sin(PULSE_FREQUENCY * time)
    rotate_angle = ROTATE_SPEED * time
    circle_color = color_morph(time)

    num_points = 100  # Number of points to draw the circle (higher number = smoother)
    wave_points = []
    for i in range(num_points):
        angle = 2 * np.pi * i / num_points
        x = (pulse_radius) * np.cos(angle)
        y = (pulse_radius) * np.sin(angle)
        x, y = rotate_point(x, y, rotate_angle)
        x += CENTER_X
        y += CENTER_Y
        wave_points.append((x, y))
    
    pygame.draw.polygon(screen, circle_color, wave_points)
    
    # Render text and draw it on top of the circle
    text_surface = font.render("Lazy Music", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(CENTER_X, CENTER_Y))
    screen.blit(text_surface, text_rect)

    # Calculate the height position of the bars to ensure they don't overlap the circle
    bar_spacing = WIDTH / NUM_BARS  # Adjust spacing to evenly distribute bars
    for i, height in enumerate(bar_heights):
        # Normalize the height to fit within the maximum bar height
        bar_height = min(MAX_BAR_HEIGHT, height)
        
        # Use a pleasant color for each bar
        bar_color = random.choice(PLEASANT_COLORS)  # Choose a pleasant color for each bar
        
        # Position bars below the circle, leaving enough space
        bar_x = i * bar_spacing
        bar_y = HEIGHT - bar_height - CIRCLE_RADIUS - CIRCLE_MARGIN
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, BAR_WIDTH, bar_height))

    # Draw stars that pop around the circle and shoot out during beats
    stars = draw_stars(stars)
    
    pygame.display.flip()

def main():
    stars = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read audio data
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)

        # Update bar heights and detect beats
        bar_heights = get_bar_heights(data)
        beat_detected, avg_volume = detect_beats(data)

        # If a beat is detected, create new stars with random velocities
        if beat_detected:
            for _ in range(STAR_COUNT):
                angle = random.uniform(0, 2 * np.pi)
                radius = CIRCLE_RADIUS + CIRCLE_MARGIN + random.uniform(0, 50)  # Random radius from the circle edge
                x = CENTER_X + radius * np.cos(angle)
                y = CENTER_Y + radius * np.sin(angle)
                star_color = random.choice(PLEASANT_COLORS)  # Use a pleasant color for each star
                velocity = STAR_VELOCITY + random.uniform(-50, 50)  # Random velocity for a more dynamic effect
                stars.append(Star(x, y, star_color, angle, velocity))
        
        # Draw the visualizer
        draw_visualizer(bar_heights, beat_detected, stars)

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()

if __name__ == "__main__":
    main()





