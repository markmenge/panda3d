#!/usr/bin/env python

from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, LineSegs, NodePath, Vec3, LPoint3

class World(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # Set initial camera position and orientation
        '''
Heading (H):
Rotates the camera around the Z-axis (like turning your head left/right).
0 degrees means the camera looks down the positive Y-axis.
Pitch (P):
Rotates the camera around the X-axis (like nodding your head up/down).
0 degrees means level.
Negative values tilt downward; positive values tilt upward.
Roll (R):
Rotates the camera around the Y-axis (like tilting your head sideways).
0 degrees means no sideways tilt.
        '''
        # camera.setPos(40, 0, 10)
        # camera.setHpr(90, 0, 0)
        camera.setPos(20, 0, 0)
        camera.setHpr(90, 0, 0)      # 0, 0, 0, looks down the y axis

        # Initialize speed, velocities, and rotational inertia
        self.speed = 1  # Base movement speed
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
            self.speed += 0.1  # Accelerate forward
        if self.key_map[","]:
            self.speed -= 0.1  # Decelerate (can go backward)

        # Calculate velocity in the direction the camera is pointing
        forward = camera.getQuat(render).getForward()  # Forward direction based on camera's quaternion
        velocity = forward * self.speed

        # Update camera position based on velocity
        movement = velocity * dt
        camera.setPos(camera.getPos() + movement)

        self.draw_axes()

        return task.cont

        """Update camera position and rotation based on user input."""
        dt = max(globalClock.getDt(), 0.001)  # Clamp dt to avoid tiny values

        # Adjust rotational velocities based on key inputs
        if self.key_map["arrow_left"]:
            self.yaw_velocity += 10 * dt  # Turn left
        if self.key_map["arrow_right"]:
            self.yaw_velocity -= 10 * dt  # Turn right
        if self.key_map["arrow_up"]:
            self.pitch_velocity += 10 * dt  # Look up
        if self.key_map["arrow_down"]:
            self.pitch_velocity -= 10 * dt  # Look down

        # Apply rotational inertia (gradual slowdown)
        self.yaw_velocity *= self.rotation_decay
        self.pitch_velocity *= self.rotation_decay

        # Apply rotations
        camera.setH(camera.getH() + self.yaw_velocity)
        camera.setP(camera.getP() + self.pitch_velocity)

        # Adjust velocity based on camera direction and acceleration
        if self.key_map["."]:
            forward = camera.getRelativeVector(render, Vec3(0, 1, 0))  # Camera's forward direction
            self.velocity += forward * 0.1  # Accelerate forward
        if self.key_map[","]:
            forward = camera.getRelativeVector(render, Vec3(0, 1, 0))  # Camera's forward direction
            self.velocity -= forward * 0.1  # Decelerate or move backward

        # Apply velocity to camera position
        movement = self.velocity * dt
        camera.setPos(camera.getPos() + movement)

        # Debugging output
        print(f"dt: {dt:.6f}, Velocity: {self.velocity}")
        print(f"Camera Position: {camera.getPos()}, HPR: {camera.getHpr()}\n")

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
            "[Arrow Keys]: Rotate/Move\n"
            "[.]: Accelerate forward\n"
            "[,]: Decelerate/Move backward\n"
            "[?]: Toggle this help\n"
        )
        text_node = TextNode("help_text")
        text_node.setText(help_text)
        text_node.setAlign(TextNode.ALeft)
        self.help_text_node = aspect2d.attachNewNode(text_node)
        self.help_text_node.setScale(0.05)
        self.help_text_node.setPos(-1.2, 0, 0.8)  # Adjust position on screen
        self.help_text_node.hide()  # Start with help text hidden

    def init_sky(self):
        """Render the sky."""
        sky = loader.loadModel("models/solar_sky_sphere")
        sky.setTexture(loader.loadTexture("models/stars_1k_tex.jpg"), 1)
        sky.setScale(1000)
        sky.reparentTo(render)

    def create_planets(self):
        """Render the planets in the solar system."""
        planet_data = [
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

        for name, orbit, size, texture in planet_data:
            root = render.attachNewNode(f'orbit_root_{name}')
            model = loader.loadModel("models/planet_sphere")
            model.setTexture(loader.loadTexture(f"models/{texture}"), 1)
            model.setScale(size * 0.6)
            model.setPos(orbit * 10, 0, 0)
            model.reparentTo(root)

w = World()
w.run()
