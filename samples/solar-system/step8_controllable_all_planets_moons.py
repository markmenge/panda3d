#!/usr/bin/env python
# filename: step7_controllable_all_planets_with_help.py
# Author: Shao Zhang and Phil Saltzman
# Modified by: Mark (ChatGPT)
# pip install panda3d

from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, LineSegs, NodePath, Vec3, LPoint3

class World(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Set initial camera position and orientation
        camera.setPos(0, 0, 60)
        camera.setHpr(0, -90, 0)

        # Initialize movement and rotation variables
        self.speed = 0
        self.velocity = Vec3(0, 0, 0)
        self.yaw_velocity = 0
        self.pitch_velocity = 0
        self.rotation_decay = 0.97

        # Key map for user controls
        self.key_map = {
            "arrow_up": False,
            "arrow_down": False,
            "arrow_left": False,
            "arrow_right": False,
            ".": False,
            ",": False,
        }
        for key in self.key_map.keys():
            self.accept(key, self.update_key_map, [key, True])
            self.accept(f"{key}-up", self.update_key_map, [key, False])
        self.accept("?", self.toggle_help)
        self.accept("space", self.stop_flying)

        self.taskMgr.add(self.update_task, "update_task")

        self.init_sky()
        self.create_planets()

        self.help_text_node = None
        self.help_visible = False
        self.create_help_text()
        self.draw_axes()

    def update_key_map(self, key, value):
        self.key_map[key] = value

    def draw_axes(self):
        """Draw the X (red), Y (green), and Z (blue) axes."""
        axes = LineSegs()
        axes.setColor(1, 0, 0, 1)
        axes.moveTo(0, 0, 0)
        axes.drawTo(10, 0, 0)

        axes.setColor(0, 1, 0, 1)
        axes.moveTo(0, 0, 0)
        axes.drawTo(0, 10, 0)

        axes.setColor(0, 0, 1, 1)
        axes.moveTo(0, 0, 0)
        axes.drawTo(0, 0, 10)

        axis_node = axes.create()
        NodePath(axis_node).reparentTo(render)

    def update_task(self, task):
        dt = max(globalClock.getDt(), 0.001)

        # Update rotation velocities based on arrow key inputs
        if self.key_map["arrow_left"]:
            self.yaw_velocity += 1 * dt
        if self.key_map["arrow_right"]:
            self.yaw_velocity -= 1 * dt
        # Invert pitch for a more natural flying feel:
        if self.key_map["arrow_up"]:
            self.pitch_velocity -= 0.1 * dt
        if self.key_map["arrow_down"]:
            self.pitch_velocity += 0.1 * dt

        # Apply rotational inertia (gradual decay)
        self.yaw_velocity *= self.rotation_decay
        self.pitch_velocity *= self.rotation_decay

        camera.setH(camera.getH() + self.yaw_velocity)
        camera.setP(camera.getP() + self.pitch_velocity)

        # Update speed based on forward/backward keys
        if self.key_map["."]:
            self.speed += 0.1
        if self.key_map[","]:
            self.speed -= 0.1

        # Calculate movement vector and update camera position
        forward = camera.getQuat(render).getForward()
        velocity = forward * self.speed
        movement = velocity * dt
        camera.setPos(camera.getPos() + movement)

        return task.cont

    def stop_flying(self):
        """Stop all movement when space is pressed."""
        self.speed = 0
        self.yaw_velocity = 0
        self.pitch_velocity = 0

    def toggle_help(self):
        self.help_visible = not self.help_visible
        if self.help_visible:
            self.help_text_node.show()
        else:
            self.help_text_node.hide()

    def create_help_text(self):
        help_text = (
            "[Arrow Keys]: Navigation (up/down inverted).\n"
            "[.]: Go forward.\n"
            "[,]: Go backward.\n"
            "[Space]: Stop movement.\n"
            "[?]: Toggle this help screen.\n\n"
        )
        text_node = TextNode("help_text")
        text_node.setText(help_text)
        text_node.setAlign(TextNode.ALeft)
        self.help_text_node = base.a2dTopLeft.attachNewNode(text_node)
        self.help_text_node.setScale(0.05)
        self.help_text_node.setPos(0.05, 0, -0.05)

    def init_sky(self):
        """Render the starry sky."""
        sky = loader.loadModel("models/solar_sky_sphere")
        sky.setTexture(loader.loadTexture("models/stars_1k_tex.jpg"), 1)
        sky.setScale(1000)
        sky.reparentTo(render)

    def create_planets(self):
        """Create the Sun, planets revolving around it, and moons revolving around their planets."""
        planet_data = [
            # (Name, Orbit Distance, Size, Texture Filename)
            ("Sun", 0, 2, "sun_1k_tex.jpg"),
            ("Mercury", 0.38, 0.385, "mercury_1k_tex.jpg"),
            ("Venus", 0.72, 0.923, "venus_1k_tex.jpg"),
            ("Earth", 1.0, 1.0, "earth_1k_tex.jpg"),
            ("Mars", 1.52, 0.515, "mars_1k_tex.jpg"),
            ("Jupiter", 5.2, 11.2, "jupiter_1k_tex.jpg"),
            ("Saturn", 9.5, 9.5, "saturn_1k_tex.jpg"),
            ("Uranus", 19.8, 4.0, "uranus_1k_tex.jpg"),
            ("Neptune", 30.1, 3.9, "neptune_1k_tex.jpg"),
        ]

        # Spin durations (in seconds) for self-rotation of each body.
        spin_durations = {
            "Sun": 20,
            "Mercury": 8,
            "Venus": 12,
            "Earth": 10,
            "Mars": 11,
            "Jupiter": 15,
            "Saturn": 18,
            "Uranus": 20,
            "Neptune": 22,
        }

        moon_data = {
            "Earth": [("Moon", 0.2, 0.1, "moon_1k_tex.jpg")],
            "Mars": [("Phobos", 0.2, 0.05, "phobos_1k_tex.jpg"),
                     ("Deimos", 0.3, 0.04, "deimos_1k_tex.jpg")],
            "Jupiter": [("Io", 0.5, 0.2, "generic_moon_1k_tex.jpg")],
            "Saturn": [("Titan", 0.6, 0.2, "generic_moon_1k_tex.jpg")],
        }

        for name, orbit, size, texture in planet_data:
            print(f"Creating planet: {name}")
            # Create a root node for the planet's orbit around the Sun.
            root = render.attachNewNode(f'orbit_root_{name}')
            model = loader.loadModel("models/planet_sphere")
            model.setTexture(loader.loadTexture(f"models/{texture}"), 1)
            model.setScale(size * 0.6)
            if orbit > 0:
                model.setPos(orbit * 10, 0, 0)
            else:
                model.setPos(0, 0, 0)
            model.reparentTo(root)

            # Animate self-rotation (spin) for the planet or Sun.
            spin_duration = spin_durations.get(name, 10)
            spin_interval = model.hprInterval(spin_duration, (360, 0, 0))
            spin_interval.loop()

            # Animate revolution around the Sun (skip for the Sun itself).
            if orbit > 0:
                orbit_interval = root.hprInterval(orbit * 20, (360, 0, 0))
                orbit_interval.loop()

            # Attach moons if defined for this planet.
            if name in moon_data:
                for moon_name, moon_orbit, moon_size, moon_texture in moon_data[name]:
                    print(f"  Adding moon: {moon_name} to planet: {name}")
                    # Create a node for the moon's orbit around the planet.
                    moon_root = model.attachNewNode(f'orbit_root_{moon_name}')
                    moon_model = loader.loadModel("models/planet_sphere")
                    moon_model.setTexture(loader.loadTexture(f"models/{moon_texture}"), 1)
                    moon_model.setScale(moon_size * 0.6)
                    moon_model.setPos(moon_orbit * 10, 0, 0)
                    moon_model.reparentTo(moon_root)
                    # Animate the moon's orbit around the planet.
                    moon_orbit_interval = moon_root.hprInterval(moon_orbit * 5, (360, 0, 0))
                    moon_orbit_interval.loop()

w = World()
w.run()
