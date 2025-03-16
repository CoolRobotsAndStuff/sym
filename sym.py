import pygame
from dataclasses import dataclass 
from random import random
from copy import deepcopy
from math import sqrt, pow, atan2, cos, sin

@dataclass
class Particle:
    position: [float, float]
    velocity: [float, float]
    acceleration: [float, float]
    mass: float
    radious: float
    colour: [float, float, float]
    will_be_deleted: bool = False


NPARTICLES = 100
WIDTH = 1000
HEIGHT = 1000

particles = []

def random_particle() -> Particle:
    radious = 10*random()
    density = 500000*random() + 1000
    return Particle(
        position=[random() * WIDTH, random()*HEIGHT],
        velocity=[(random() - 0.5) * 0.02, (random() - 0.5) * 0.02],
        acceleration=[0, 0],
        mass = radious * density,
        radious = radious,
        colour = (random()*255, random()*255, random()*255)
    )


def gravitational_force(p1, p2):
    position_diff = (p2.position[0] - p1.position[0], 
                     p2.position[1] - p1.position[1])    

    square_distance = pow(position_diff[0], 2) + pow(position_diff[1], 2)
    direction = atan2(position_diff[1], position_diff[0])

    G = 6.67430e-11
    force = G * (p1.mass * p2.mass) / square_distance
    
    force_x = cos(direction) * force
    force_y = sin(direction) * force
    return [force_x, force_y]

zoom = 1
cam_pos = [0, 0]
follow_particle = None
show_big_particles = False
show_density = False

if __name__ == "__main__":
    for _ in range(NPARTICLES):
        particles.append(random_particle())

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    dt = 0
    time = 1

    while running:
        screen_width, screen_height = screen.get_size()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == "+":
                    zoom *= 1.1
                elif pygame.key.name(event.key) == "-":
                    zoom *= 0.9
                elif pygame.key.name(event.key) == "t":
                    time *= 1.1
                elif pygame.key.name(event.key) == "r":
                    time *= 0.9
                elif pygame.key.name(event.key) == "n":
                    if follow_particle == None:
                        follow_particle = 0
                    else:
                        follow_particle += 1
                        follow_particle %= len(particles)-1
                elif pygame.key.name(event.key) == "s":
                    if show_big_particles:
                        show_big_particles = False 
                    else:
                        show_big_particles = True

                elif pygame.key.name(event.key) == "m":
                    if show_density:
                        show_density = False
                    else:
                        show_density = True

        if follow_particle is not None:
            follow_particle %= len(particles)-1
            cam_pos = deepcopy(particles[follow_particle].position)
            # cam_pos[0] -= screen_width // 2
            # cam_pos[1] -= screen_height // 2



        cam_vel = 10 / zoom
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l]:
            cam_pos[0] += cam_vel
            follow_particle = None
        if keys[pygame.K_h]:
            cam_pos[0] -= cam_vel
            follow_particle = None
        if keys[pygame.K_j]:
            cam_pos[1] += cam_vel
            follow_particle = None
        if keys[pygame.K_k]:
            cam_pos[1] -= cam_vel
            follow_particle = None


        screen.fill("#181818")

        colliding_particles = []
        for p_index, p in enumerate(particles):
            collided = False
            for other_index, other_p in enumerate(particles):
                if p_index == other_index:
                    continue

                if p.will_be_deleted or other_p.will_be_deleted: 
                    continue

                difference = other_p.position[0] - p.position[0], other_p.position[1] - p.position[1]
                dist = sqrt(pow(difference[0], 2) + pow(difference[1], 2))
                if p.radious + other_p.radious > dist:
                    collided = True
                    wsum = p.mass + other_p.mass
                    weight1 = p.mass / wsum
                    weight2 = other_p.mass / wsum
                    print("weight1:", weight1)
                    print("weight2:", weight2)
                    print("sum:", weight2 + weight1)
                    new_p = Particle(position=[
                                        weight1 * p.position[0] + weight2 * other_p.position[0],
                                        weight1 * p.position[1] + weight2 * other_p.position[1]
                                     ],
                                     velocity=[
                                        weight1 * p.velocity[0] + weight2 * other_p.velocity[0],
                                        weight1 * p.velocity[1] + weight2 * other_p.velocity[1]
                                     ],
                                     acceleration=[
                                        weight1 * p.acceleration[0] + weight2 * other_p.acceleration[0],
                                        weight1 * p.acceleration[1] + weight2 * other_p.acceleration[1]
                                     ],
                                     mass = p.mass + other_p.mass,
                                     #radious = sqrt(pow(p.radious, 2) + pow(other_p.radious, 2)) * 0.8, # planet gets slightly more compressed maybe?
                                     radious = max(p.radious, other_p.radious),
                                     colour = [
                                        p.colour[0] * weight1 + other_p.colour[0] * weight2,
                                        p.colour[1] * weight1 + other_p.colour[1] * weight2,
                                        p.colour[2] * weight1 + other_p.colour[2] * weight2,
                                     ]
                    )
                    print(new_p)
                    colliding_particles.append(new_p)
                    if follow_particle == p_index or follow_particle == other_index:
                        follow_particle = len(colliding_particles)-1
                    particles[other_index].will_be_deleted = True
                    particles[p_index].will_be_deleted = True

            if not collided:
                colliding_particles.append(deepcopy(p))

        particles = []
        for p in colliding_particles:
            if not p.will_be_deleted:
                particles.append(p)

        new_particles = []
        for p_index, p in enumerate(particles):
            forces = []
            total_force = [0, 0]
            for other_index, other_p in enumerate(particles):
                if p_index == other_index:
                    continue
                f = gravitational_force(p, other_p)
                total_force[0] += f[0]
                total_force[1] += f[1]


            if len(particles) > 1: 
                total_force[0] /= len(particles)-1
                total_force[1] /= len(particles)-1
            

            new_p = deepcopy(p)
            new_p.acceleration[0] = total_force[0] / new_p.mass * dt
            new_p.acceleration[1] = total_force[1] / new_p.mass * dt

            new_particles.append(new_p)


            new_p.velocity[0] += new_p.acceleration[0] * dt
            new_p.velocity[1] += new_p.acceleration[1] * dt

            new_p.position[0] += new_p.velocity[0] * dt
            new_p.position[1] += new_p.velocity[1] * dt
            
            pos = [((new_p.position[0] - cam_pos[0]) * zoom) + screen_width // 2 , ((new_p.position[1]- cam_pos[1]) * zoom) + screen_height //2   ]
            
            
            if show_density: 
                max_mass = 0
                for p1 in particles:
                    max_mass = max(max_mass, p1.mass)

                mass = new_p.mass 
                col = (255 * (mass/max_mass), 0, 255 - (255 * (mass/max_mass)))
            else:
                col = p.colour

            if not show_big_particles:
                pygame.draw.circle(screen, col, pos, new_p.radious * zoom)
            else:
                pygame.draw.circle(screen, col, pos, new_p.radious)

        particles = new_particles

        pygame.display.flip()
        dt = clock.tick(60) * 10 * time
    pygame.quit()
