"""Defines a more Pythonic interface for specifying the joint names.

The best way to re-generate this snippet for a new robot is to use the
`sim/scripts/print_joints.py` script. This script will print out a hierarchical
tree of the various joint names in the robot.
"""

import textwrap
from abc import ABC
from typing import Dict, List, Tuple, Union


class Node(ABC):
    @classmethod
    def children(cls) -> List["Union[Node, str]"]:
        return [
            attr
            for attr in (getattr(cls, attr) for attr in dir(cls) if not attr.startswith("__"))
            if isinstance(attr, (Node, str))
        ]

    @classmethod
    def joints(cls) -> List[str]:
        return [
            attr
            for attr in (getattr(cls, attr) for attr in dir(cls) if not attr.startswith("__"))
            if isinstance(attr, str)
        ]

    @classmethod
    def joints_motors(cls) -> List[Tuple[str, str]]:
        joint_names: List[Tuple[str, str]] = []
        for attr in dir(cls):
            if not attr.startswith("__"):
                attr2 = getattr(cls, attr)
                if isinstance(attr2, str):
                    joint_names.append((attr, attr2))

        return joint_names

    @classmethod
    def all_joints(cls) -> List[str]:
        leaves = cls.joints()
        for child in cls.children():
            if isinstance(child, Node):
                leaves.extend(child.all_joints())
        return leaves

    def __str__(self) -> str:
        parts = [str(child) for child in self.children()]
        parts_str = textwrap.indent("\n" + "\n".join(parts), "  ")
        return f"[{self.__class__.__name__}]{parts_str}"


class LeftLeg(Node):
    hip_pitch = "Left hip pitch motor inner"
    hip_yaw = "Left hip yaw motor inner"
    hip_roll = "Left roll motor inner"
    knee_pitch = "Left knee motor inner"
    ankle_pitch = "left Ankle motor inner"
    ankle_roll = "Left foot motor"


class RightLeg(Node):
    hip_pitch = "Hip pitch motor inner"
    hip_yaw = "Hip yaw motor inner"
    hip_roll = "Roll Motor inner"
    knee_pitch = "Knee motor inner"
    ankle_pitch = "Ankle motor inner"
    ankle_roll = "Foot motor fixed"


class Legs(Node):
    left = LeftLeg()
    right = RightLeg()


class Stompy(Node):
    legs = Legs()

    @classmethod
    def default_positions(cls) -> Dict[str, float]:
        return {}

    @classmethod
    def default_standing(cls) -> Dict[str, float]:
        return {
            Stompy.legs.left.hip_pitch: .346,
            Stompy.legs.left.hip_roll: 0.,
            Stompy.legs.left.hip_yaw: 0.0,
            Stompy.legs.left.knee_pitch: 0.597,
            Stompy.legs.left.ankle_pitch: 0.691,
            Stompy.legs.left.ankle_roll: 0,
            Stompy.legs.right.hip_pitch: 3.14,
            Stompy.legs.right.hip_roll: 0,
            Stompy.legs.right.hip_yaw: 3.14,
            Stompy.legs.right.knee_pitch:  -0.534,
            Stompy.legs.right.ankle_pitch: -0.9432,
            Stompy.legs.right.ankle_roll: 0.22,
        }

    @classmethod
    def default_limits(cls) -> Dict[str, Dict[str, float]]:
        return {
            Stompy.legs.left.hip_pitch: {
                "lower": -1.22,
                "upper": 1.346,
            },
            Stompy.legs.left.hip_yaw: {
                "lower": -1.08,
                "upper":    0.98,
            },
            Stompy.legs.left.hip_roll: {
                "lower": -0.15,
                "upper": 0.15,
            },
            Stompy.legs.left.knee_pitch: {
                "lower": 0.0,
                "upper": 1.57,
            },
            Stompy.legs.left.ankle_pitch: {
                "lower":   -.1,
                "upper":   1,
            },
            Stompy.legs.left.ankle_roll: {
                "lower": -0.5,
                "upper":  .5,
            },
            Stompy.legs.right.hip_pitch: {
                "lower":  2.14,
                "upper":   4.14
            },
            Stompy.legs.right.hip_yaw: {
                "lower":  2.14,
                "upper": 4.14,
            },
            Stompy.legs.right.hip_roll: {
                "lower":  -0.15,
                "upper": 0.15,
            },
            Stompy.legs.right.knee_pitch: {
                "lower": -1.57,
                "upper": 0,  
            },
            Stompy.legs.right.ankle_pitch: {
                "lower": -1.57,   
                "upper":  0.0,  
            },
            Stompy.legs.right.ankle_roll: {
                "lower": -0.45,
                "upper":  0.45,
            },
        }

    # p_gains
    @classmethod
    def stiffness(cls) -> Dict[str, float]:
        return {
            "Hip pitch": 250,
            "hip pitch": 250,
            "yaw": 150,
            "Roll": 150,
            "roll": 150,
            "knee": 150,
            "Knee": 150,
            "Ankle motor": 45,
            "foot": 45,
            "Foot": 45,
        }

    # d_gains
    @classmethod
    def damping(cls) -> Dict[str, float]:
        return {
            "Hip pitch": 15,
            "hip pitch": 15,
            "yaw": 10,
            "Roll": 10,
            "roll": 10,
            "knee": 10,
            "Knee": 10,
            "Ankle motor": 3,
            "foot": 3,
            "Foot": 3,
        }

    # pos_limits
    @classmethod
    def effort(cls) -> Dict[str, float]:
        # return {
        #     "hip pitch": 150,
        #     "hip yaw": 90,
        #     "hip roll": 90,
        #     "knee pitch": 90,
        #     "ankle pitch": 24,
        #     "ankle roll": 24,
        # }
        return { 
            "Hip pitch": 150,
            "hip pitch": 150,
            "yaw":  90,
            "Roll": 90,
            "roll": 90, 
            "knee":  90,
            "Knee":  90,
            "Ankle motor":  24,
            "foot":     24,
            "Foot":     24,
        }

    # vel_limits
    @classmethod
    def velocity(cls) -> Dict[str, float]:
        # return {
        #     "hip pitch": 40,
        #     "hip yaw": 40,
        #     "hip roll": 40,
        #     "knee pitch": 40,
        #     "ankle pitch": 24,
        #     "ankle roll": 24,
        # }
        return { 
            "Hip pitch":  40,
            "hip pitch":    40,
            "yaw":  40,
            "Roll": 40,
            "roll":  40,
            "knee":  40,    
            "Knee":  40,
            "Ankle motor":  24,
            "foot":         24,
            "Foot":         24,
        }

    @classmethod
    def friction(cls) -> Dict[str, float]:
        return { 
            "Hip pitch": 0,
            "hip pitch": 0,
            "yaw":  0,
            "Roll":   0,   
            "roll":   0,   
            "knee":  0,   
            "Knee":  0, 
            "Ankle motor":  0,
            "foot":     0.1,
            "Foot":     0.1,
        }


def print_joints() -> None:
    joints = Stompy.all_joints()
    assert len(joints) == len(set(joints)), "Duplicate joint names found!"
    print(Stompy())


if __name__ == "__main__":
    # python -m sim.stompy.joints
    print_joints()