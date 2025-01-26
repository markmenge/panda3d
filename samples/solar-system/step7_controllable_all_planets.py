#!/usr/bin/env python
# filename: step7_controllable_all_planets_with_help.py
# Author: Shao Zhang and Phil Saltzman

from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, LineSegs, NodePath, Vec3, LPoint3

class World(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Set initial camera position and orientation
        camera.setPos(20, 0, 0)
        camera.setHpr(90, 0, 0)  # 0, 0, 0, looks down the y axis

        # Initialize speed, velocities, and rotational inertia
        self.speed = 0  # Base movement speed
        self.velocity = Vec3(0, 0, 0)  # Linear velocity
        self.yaw_velocity = 0  # Yaw rotation velocity (left/right)
        self.pitch_velocity = 0  # Pitch rotation velocity (up/down)
        self.rotation_decay = 0.97  # Decay factor for rotational inertia

        # Key map for user controls
        self.key_map = {
            "arrow_up": False,    # Increase pitch (look up)
            "arrow_down": False,  # Decrease pitch (look down)
            "arrow_left": False,  # Increase yaw (turn left)
            "arrow_right": False, # Decrease yaw (turn right)
            ".": False,           # Accelerate forward
            ",": False,           # Decelerate/backward
        }

        # Add bindings for controls and toggle help
        for key in self.key_map.keys():
            self.accept(key, self.update_key_map, [key, True])
            self.accept(f"{key}-up", self.update_key_map, [key, False])
        self.accept("?", self.toggle_help)

        # Add update task
        self.taskMgr.add(self.update_task, "update_task")

        # Render the sky and planets
        self.init_sky()
        self.create_planets()

        # Help text setup
        self.help_text_node = None
        self.help_visible = False
        self.create_help_text()  # Prepare the help text
        self.draw_axes()

    def update_key_map(self, key, value):
        """Update the state of the key map."""
        self.key_map[key] = value

    def draw_axes(self):
        """Draw X, Y, and Z axes in the scene."""
        axes = LineSegs()
        axes.setColor(1, 0, 0, 1)  # Red for X-axis
        axes.moveTo(0, 0, 0)
        axes.drawTo(10, 0, 0)  # Positive X-axis

        axes.setColor(0, 1, 0, 1)  # Green for Y-axis
        axes.moveTo(0, 0, 0)
        axes.drawTo(0, 10, 0)  # Positive Y-axis

        axes.setColor(0, 0, 1, 1)  # Blue for Z-axis
        axes.moveTo(0, 0, 0)
        axes.drawTo(0, 0, 10)  # Positive Z-axis

        # Create a NodePath for the axes and attach to render
        axis_node = axes.create()
        NodePath(axis_node).reparentTo(render)

    def update_task(self, task):
        """Update camera position and rotation based on user input."""
        dt = max(globalClock.getDt(), 0.001)  # Clamp dt to avoid tiny values

        # Adjust rotational velocities based on key inputs
        if self.key_map["arrow_left"]:
            self.yaw_velocity += 1 * dt  # Turn left
        if self.key_map["arrow_right"]:
            self.yaw_velocity -= 1 * dt  # Turn right
        if self.key_map["arrow_up"]:
            self.pitch_velocity += 1 * dt  # Look up
        if self.key_map["arrow_down"]:
            self.pitch_velocity -= 1 * dt  # Look down

        # Apply rotational inertia (gradual slowdown)
        self.yaw_velocity *= self.rotation_decay
        self.pitch_velocity *= self.rotation_decay

        # Apply rotations
        camera.setH(camera.getH() + self.yaw_velocity)
        camera.setP(camera.getP() + self.pitch_velocity)

        # Adjust speed based on user input
        if self.key_map["."]:
            self.speed += 0.1  # forward
        if self.key_map[","]:
            self.speed = self.speed - 0.1  # backward

        # Calculate velocity in the direction the camera is pointing
        forward = camera.getQuat(render).getForward()  # Forward direction based on camera's quaternion
        velocity = forward * self.speed

        # Update camera position based on velocity
        movement = velocity * dt
        camera.setPos(camera.getPos() + movement)

        return task.cont

    def toggle_help(self):
        """Toggle the help text on or off."""
        self.help_visible = not self.help_visible
        if self.help_visible:
            self.help_text_node.show()
        else:
            self.help_text_node.hide()

    def create_help_text(self):
        """Create the on-screen help text."""
        help_text = (
            "[Arrow Keys]: Navigation.\n"
            "[.]: Go forward.\n"
            "[,]: Go backward.\n"
            "[?]: Toggle this help screen.\n\n"
        )
        text_node = TextNode("help_text")
        text_node.setText(help_text)
        text_node.setAlign(TextNode.ALeft)  # Left-aligned text
        self.help_text_node = base.a2dTopLeft.attachNewNode(text_node)  # Parent to top-left corner
        self.help_text_node.setScale(0.05)  # Adjust text size
        self.help_text_node.setPos(0.05, 0, -0.05)  # Slight offset from the top-left

    def init_sky(self):
        """Render the sky."""
        sky = loader.loadModel("models/solar_sky_sphere")
        sky.setTexture(loader.loadTexture("models/stars_1k_tex.jpg"), 1)
        sky.setScale(1000)
        sky.reparentTo(render)

    def create_planets(self):
        """Render the planets and their moons in the solar system."""
        planet_data = [
            # ("Name", Orbit Distance (in AU scaled), Size (relative to Sun), Texture Filename)
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

        moon_data = {
            "Earth": [("Moon", 0.1, 0.1, "moon_1k_tex.jpg")],  # Earth's Moon
            "Mars": [("Phobos", 0.2, 0.05, "phobos_1k_tex.jpg"),  # Phobos
                    ("Deimos", 0.3, 0.04, "deimos_1k_tex.jpg")],  # Deimos
            "Jupiter": [("Io", 0.5, 0.2, "generic_moon_1k_tex.jpg"),        # Io
                        ("Europa", 0.6, 0.15, "generic_moon_1k_tex.jpg"),
                        ("Ganymede", 0.7, 0.25, "generic_moon_1k_tex.jpg"),
                        ("Callisto", 0.8, 0.22, "generic_moon_1k_tex.jpg")],
            "Saturn": [("Titan", 0.6, 0.2, "generic_moon_1k_tex.jpg")],  # Titan
        }

        for name, orbit, size, texture in planet_data:
            # Create a root node for the planet to allow for orbiting behavior
            root = render.attachNewNode(f'orbit_root_{name}')
            
            # Load the 3D model for the planet and apply its texture
            model = loader.loadModel("models/planet_sphere")
            model.setTexture(loader.loadTexture(f"models/{texture}"), 1)
            
            # Scale the planet's size (arbitrary scaling factor of 0.6 for the demo)
            model.setScale(size * 0.6)
            
            # Position the planet at its orbit distance (scaled AU for visual clarity)
            model.setPos(orbit * 10, 0, 0)
            
            # Attach the planet model to its orbit root
            model.reparentTo(root)

            # Add moons if this planet has any
            if name in moon_data:
                for moon_name, moon_orbit, moon_size, moon_texture in moon_data[name]:
                    moon_root = root.attachNewNode(f'orbit_root_{moon_name}')
                    moon_model = loader.loadModel("models/planet_sphere")
                    moon_model.setTexture(loader.loadTexture(f"models/{moon_texture}"), 1)
                    moon_model.setScale(moon_size * 0.6)
                    moon_model.setPos(moon_orbit * 10, 0, 0)
                    moon_model.reparentTo(moon_root)


w = World()
w.run()
