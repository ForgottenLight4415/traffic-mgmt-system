import random
import time
import threading
import pygame
import sys

# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 20

signals = []
noOfSignals = 4
simTime = 300
timeElapsed = 0

currentGreen = 0
currentYellow = 0
emergencyPresent = False
lock = threading.Lock()  # Lock for thread synchronization

# Vehicle average speeds
speeds = {'car': 2.5, 'bus': 2.0, 'truck': 1.8, 'bike': 3.0, 'ambulance': 4.0}

# Coordinates for vehicles
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike', 4: 'ambulance'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Stop line coordinates
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Signal and timer coordinates
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(500, 230), (780, 230), (780, 570), (500, 570)]  # Moved to the left of signals
densityCoords = [(480, 210), (860, 210), (860, 550), (480, 550)]  # For showing vehicle density

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleType, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleType = vehicleType
        self.speed = speeds[vehicleType]
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = False
        vehicles[direction][lane].append(self)
        self.stop = defaultStop[direction]
        self.index = len(vehicles[direction][lane]) - 1

        path = f"images/{direction}/{vehicleType}.png"
        self.image = pygame.image.load(path)
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        print(f"DEBUG: Vehicle {self.vehicleType} at lane {self.lane}, direction {self.direction}")
        print(f"DEBUG: Current position (x, y): ({self.x}, {self.y})")

        if self.index > 0:  # If there's a vehicle in front
            front_vehicle = vehicles[self.direction][self.lane][self.index - 1]
            print(f"DEBUG: Front vehicle position (x, y): ({front_vehicle.x}, {front_vehicle.y})")
            if self.direction in ['right', 'left']:
                if self.direction == 'right':
                    if self.x + self.image.get_width() + 20 < front_vehicle.x:
                        self.update_position()
                elif self.direction == 'left':
                    if self.x - 20 > front_vehicle.x + front_vehicle.image.get_width():
                        self.update_position()
            elif self.direction in ['up', 'down']:
                if self.direction == 'down':
                    if self.y + self.image.get_height() + 20 < front_vehicle.y:
                        self.update_position()
                elif self.direction == 'up':
                    if self.y - 20 > front_vehicle.y + front_vehicle.image.get_height():
                        self.update_position()
        else:
            self.update_position()

    def update_position(self):
        if self.direction == 'right':
            if not self.crossed and self.x + self.image.get_width() >= stopLines[self.direction]:
                self.x = stopLines[self.direction] - self.image.get_width()
            else:
                self.x += self.speed
                if self.x > stopLines[self.direction]:
                    self.crossed = True
        elif self.direction == 'down':
            if not self.crossed and self.y + self.image.get_height() >= stopLines[self.direction]:
                self.y = stopLines[self.direction] - self.image.get_height()
            else:
                self.y += self.speed
                if self.y > stopLines[self.direction]:
                    self.crossed = True
        elif self.direction == 'left':
            if not self.crossed and self.x <= stopLines[self.direction]:
                self.x = stopLines[self.direction]
            else:
                self.x -= self.speed
                if self.x < stopLines[self.direction]:
                    self.crossed = True
        elif self.direction == 'up':
            if not self.crossed and self.y <= stopLines[self.direction]:
                self.y = stopLines[self.direction]
            else:
                self.y -= self.speed
                if self.y < stopLines[self.direction]:
                    self.crossed = True


def initialize_signals():
    for _ in range(noOfSignals):
        signals.append(TrafficSignal(defaultRed, defaultYellow, defaultGreen))


def calculate_priority():
    global currentGreen, emergencyPresent
    with lock:  # Synchronize access to shared variables
        max_density = 0
        emergency_present = False
        new_signal = currentGreen

        for i, direction in enumerate(['right', 'down', 'left', 'up']):
            # Calculate density for each direction
            density = sum(len(lane) for key, lane in vehicles[direction].items() if key != 'crossed')
            print(f"DEBUG: Direction {direction}, Density: {density}")

            # Check if an ambulance is present in the current direction
            if any(vehicle.vehicleType == 'ambulance' for key, lane in vehicles[direction].items() if key != 'crossed' for vehicle in lane):
                emergency_present = True
                new_signal = i
                break

            # Find the direction with the highest density
            if density > max_density:
                max_density = density
                new_signal = i

        # Update global variables
        emergencyPresent = emergency_present
        if not emergency_present:
            print(f"DEBUG: Priority calculated. Switching to direction: {directionNumbers[new_signal]}")
            currentGreen = new_signal

def update_signals():
    global currentGreen, timeElapsed, emergencyPresent

    while timeElapsed < simTime:
        with lock:  # Synchronize updates to signals
            print(f"DEBUG: Time elapsed: {timeElapsed}")
            print(f"DEBUG: Current green signal: {currentGreen}")
            print(f"DEBUG: Emergency present: {emergencyPresent}")

            # Handle emergency (ambulance detected)
            if emergencyPresent:
                print(f"DEBUG: Ambulance detected. Turning signal {currentGreen} green.")
                signals[currentGreen].green = defaultGreen
                signals[currentGreen].yellow = 0
                signals[currentGreen].red = 0
                emergencyPresent = False
            else:
                # Decrement green timer for the current signal
                if signals[currentGreen].green > 0:
                    signals[currentGreen].green -= 1
                    print(f"DEBUG: Signal {currentGreen} green timer: {signals[currentGreen].green}")
                elif signals[currentGreen].yellow > 0:
                    # Switch to yellow if green timer expires
                    signals[currentGreen].yellow -= 1
                    print(f"DEBUG: Signal {currentGreen} yellow timer: {signals[currentGreen].yellow}")
                else:
                    # Calculate the next signal based on priority
                    calculate_priority()
                    signals[currentGreen].green = defaultGreen
                    signals[currentGreen].yellow = defaultYellow
                    signals[currentGreen].red = defaultRed
                    print(f"DEBUG: Switching to signal {currentGreen}")

        timeElapsed += 1
        time.sleep(1)

def generate_vehicles():
        ambulance_generated = False  # Flag to track if an ambulance has been generated
        while True:
            if not ambulance_generated:
                vehicle_type = 4  # Ambulance
                direction_number = random.randint(0, 3)  # Randomly assign direction
                lane_number = random.randint(0, 2)  # Randomly assign lane
                Vehicle(lane_number, vehicleTypes[vehicle_type], directionNumbers[direction_number])
                ambulance_generated = True  # Set the flag to True
            else:
                vehicle_type = random.randint(0, 3)  # Randomly generate other vehicle types (excluding ambulance)
                direction_number = random.randint(0, 3)  # Randomly assign direction
                lane_number = random.randint(0, 2)  # Randomly assign lane
                Vehicle(lane_number, vehicleTypes[vehicle_type], directionNumbers[direction_number])

            time.sleep(random.uniform(0.5, 1.5))  # Adjust the spawn interval as needed


def render_simulation(screen, background, red_signal, yellow_signal, green_signal):
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)

    with lock:  # Synchronize rendering with signal updates
        # Render signals and their timers
        for i, signal in enumerate(signals):
            timer_text = font.render("", True, (255, 255, 255))  # Initialize with an empty Surface

            if i == currentGreen:
                if signal.green > 0:
                    screen.blit(green_signal, signalCoods[i])
                    timer_text = font.render(str(signal.green), True, (0, 255, 0))  # Green timer
                elif signal.yellow > 0:
                    screen.blit(yellow_signal, signalCoods[i])
                    timer_text = font.render(str(signal.yellow), True, (255, 255, 0))  # Yellow timer
            else:
                screen.blit(red_signal, signalCoods[i])
                timer_text = font.render(str(signal.red), True, (255, 0, 0))  # Red timer

            # Display timer next to the signal
            screen.blit(timer_text, signalTimerCoods[i])

            # Display traffic density
            density = sum(len(lane) for key, lane in vehicles[directionNumbers[i]].items() if key != 'crossed')
            density_text = font.render(f"Density: {density}", True, (255, 255, 255))
            screen.blit(density_text, densityCoords[i])

    # Render vehicles
    for vehicle in simulation:
        vehicle.render(screen)
        vehicle.move()

    pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("Traffic Simulation")
    background = pygame.image.load("images/mod_int.png")
    red_signal = pygame.image.load("images/signals/red.png")
    yellow_signal = pygame.image.load("images/signals/yellow.png")
    green_signal = pygame.image.load("images/signals/green.png")

    initialize_signals()

    threading.Thread(target=generate_vehicles, daemon=True).start()
    threading.Thread(target=update_signals, daemon=True).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        render_simulation(screen, background, red_signal, yellow_signal, green_signal)


if __name__ == "__main__":
    main()
