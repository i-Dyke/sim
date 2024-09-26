"""Defines the environment configuration for the Getting up task"""

from sim.env import robot_urdf_path
from sim.envs.base.quadruped_robot_config import (  # type: ignore
    LeggedRobotCfg,
    LeggedRobotCfgPPO,
)
from sim.resources.quadruped.joints import Robot

NUM_JOINTS = len(Robot.all_joints())  # 20


class QuadrupedCfg(LeggedRobotCfg):
    """Configuration class for the Legs humanoid robot."""

    class env(LeggedRobotCfg.env):
        # change the observation dim
        frame_stack = 15
        c_frame_stack = 3
        num_single_obs = 11 + NUM_JOINTS * 3
        num_observations = int(frame_stack * num_single_obs)
        single_num_privileged_obs = 25 + NUM_JOINTS * 4 + 4  # The +4 added for quadruped...why?
        num_privileged_obs = int(c_frame_stack * single_num_privileged_obs)
        num_actions = NUM_JOINTS
        num_envs = 4096
        episode_length_s = 24  # episode length in seconds
        use_ref_actions = False

    class safety:
        # safety factors
        pos_limit = 1.0
        vel_limit = 1.0
        torque_limit = 0.85

    class asset(LeggedRobotCfg.asset):
        name = "quadruped"
        file = str(robot_urdf_path(name))

        foot_name = ["Right_Back_Lower", "Left_Back_Lower", "Right_Front_Lower", "Left_Front_Lower"]
        knee_name = ["Right_Back_Upper", "Left_Back_Upper", "Right_Front_Upper", "Left_Front_Upper"]

        termination_height = 0.13  # use termination contacts instead
        default_feet_height = 0.05
        terminate_after_contacts_on = [
            "Right_Back_Upper",
            "Left_Back_Upper",
            "Right_Front_Upper",
            "Left_Front_Upper",
            "Body",
        ]

        penalize_contacts_on = []
        self_collisions = 1  # 1 to disable, 0 to enable...bitwise filter
        flip_visual_attachments = False
        replace_cylinder_with_capsule = False
        fix_base_link = False

    class terrain(LeggedRobotCfg.terrain):
        mesh_type = "plane"
        # mesh_type = 'trimesh'
        curriculum = False
        # rough terrain only:
        measure_heights = False
        static_friction = 0.6
        dynamic_friction = 0.6
        terrain_length = 8.0
        terrain_width = 8.0
        num_rows = 10  # number of terrain rows (levels)
        num_cols = 10  # number of terrain cols (types)
        max_init_terrain_level = 10  # starting curriculum state
        # plane; obstacles; uniform; slope_up; slope_down, stair_up, stair_down
        terrain_proportions = [0.2, 0.2, 0.4, 0.1, 0.1, 0, 0]
        restitution = 0.0

    class noise:
        add_noise = False
        noise_level = 0.6  # scales other values

        class noise_scales:
            dof_pos = 0.05
            dof_vel = 0.5
            ang_vel = 0.1
            lin_vel = 0.05
            quat = 0.03
            height_measurements = 0.03  # was 0.1

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, Robot.height]
        # setting the right rotation
        # quat_from_euler_xyz(torch.tensor(1.57), torch.tensor(0), torch.tensor(-1.57))
        rot = Robot.rotation

        default_joint_angles = {k: 0.0 for k in Robot.all_joints()}

        default_positions = Robot.default_standing()
        for joint in default_positions:
            default_joint_angles[joint] = default_positions[joint]

    class control(LeggedRobotCfg.control):
        # PD Drive parameters:
        stiffness = Robot.stiffness()
        damping = Robot.damping()
        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25
        # decimation: Number of control action updates @ sim DT per policy DT
        decimation = 10  # 100hz

    class sim(LeggedRobotCfg.sim):
        dt = 0.001  # 1000 Hz
        substeps = 1  # 2
        up_axis = 1  # 0 is y, 1 is z

        class physx(LeggedRobotCfg.sim.physx):
            num_threads = 10
            solver_type = 1  # 0: pgs, 1: tgs
            num_position_iterations = 4
            num_velocity_iterations = 1
            contact_offset = 0.01  # [m]
            rest_offset = 0.0  # [m]
            bounce_threshold_velocity = 0.1  # [m/s]
            max_depenetration_velocity = 1.0
            max_gpu_contact_pairs = 2**23  # 2**24 -> needed for 8000 envs and more
            default_buffer_size_multiplier = 5
            # 0: never, 1: last sub-step, 2: all sub-steps (default=2)
            contact_collection = 2

    class domain_rand(LeggedRobotCfg.domain_rand):
        start_pos_noise = 0.00001  # changed for quad
        randomize_friction = True
        friction_range = [0.1, 2.0]

        randomize_base_mass = True  # changed for quad
        added_mass_range = [-0.0, 0.001]
        push_robots = True
        push_interval_s = 4
        max_push_vel_xy = 0.2
        max_push_ang_vel = 0.4
        dynamic_randomization = 0.05

    class commands(LeggedRobotCfg.commands):
        # Vers: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
        num_commands = 4
        resampling_time = 8.0  # time before command are changed[s]
        heading_command = True  # if true: compute ang vel command from heading error

        class ranges:
            lin_vel_x = [1.5, 5]  # min max [m/s]
            lin_vel_y = [-0.3, 0.3]  # min max [m/s]
            ang_vel_yaw = [-0.3, 0.3]  # min max [rad/s]
            heading = [-3.14, 3.14]

    class rewards:
        soft_dof_pos_limit = 0.9
        base_height_target = 0.4  # 0.25
        target_feet_height = 0.05  # m

        # Additions from Unitree for ...
        target_joint_pos_scale = 0.17  # rad, for compute_ref_state
        cycle_time = 0.4  # sec, for compute_ref_state
        tracking_sigma = 4  # 0.25 for unitree (but they used divide by tracking sigma)
        max_contact_force = 100  # forces above this value are penalized

        class scales(LeggedRobotCfg.rewards.scales):
            dof_pos_limits = -10.0

            # Override from base class (qaudruped_robot_config)

            # standing----
            # base pos
            default_joint_pos = 0.1  # 1 for the new quadruped formula for standing
            orientation = 0.25  # 1 for standing
            base_height = 0.2
            base_acc = 0.01

            # energy
            # action_smoothness = -0.002 # not used in quadruped
            torques = -1e-5
            dof_vel = -5e-4
            dof_acc = -1e-7
            collision = -1.0

            # walking ---
            # gait
            feet_air_time = 7  # 2.5
            # contact
            feet_contact_forces = -0.01
            # vel tracking , main driver of forward motion!!!
            tracking_lin_vel = 3  # 1.0
            tracking_ang_vel = 0.5  # 0.5

            # only in unitree
            lin_vel_z = -2.0
            action_rate = -0.01

            # in unitree repo (so is in our base file, but not used)---
            # action_rate = -0.0 #used in unitree only
            # stand_still = -0.0  #used in unitree only

            # NOT used in unitree----
            # joint_pos = 1.6
            # feet_clearance = 1.6
            # feet_contact_number = 1.2
            # gait
            # foot_slip = -0.05
            # feet_distance = 0.2
            # knee_distance = 0.2
            # vel tracking
            # vel_mismatch_exp = 0.5  # lin_z; ang x,y
            # track_vel_hard = 0.5
            # feet_stumble = -0.0 #not used at all

        only_positive_rewards = (
            True  # if true negative total rewards are clipped at zero (avoids early termination problems)
        )

    class normalization:
        class obs_scales:
            lin_vel = 2.0
            ang_vel = 1.0
            dof_pos = 1.0
            dof_vel = 0.05
            quat = 1.0
            height_measurements = 5.0

        clip_observations = 18.0
        clip_actions = 18.0

    class viewer:
        ref_env = 0
        pos = [4, -4, 2]
        lookat = [0, -2, 0]


class QuadrupedCfgPPO(LeggedRobotCfgPPO):
    seed = 5
    runner_class_name = "OnPolicyRunner"  # DWLOnPolicyRunner

    class policy:
        init_noise_std = 0.3  # changed for quad
        actor_hidden_dims = [512, 256, 128]
        critic_hidden_dims = [768, 256, 128]

    class algorithm(LeggedRobotCfgPPO.algorithm):
        entropy_coef = 0.001
        learning_rate = 1e-5
        num_learning_epochs = 2
        gamma = 0.994
        lam = 0.9
        num_mini_batches = 4

    class runner:
        policy_class_name = "ActorCritic"
        algorithm_class_name = "PPO"
        num_steps_per_env = 60  # per iteration
        max_iterations = 5001  # number of policy updates

        # logging
        save_interval = 100  # check for potential saves every this many iterations
        experiment_name = "Quadruped"
        run_name = ""
        # load and resume
        resume = False
        load_run = -1  # -1 = last run
        checkpoint = -1  # -1 = last saved model
        resume_path = None  # updated from load_run and chkpt