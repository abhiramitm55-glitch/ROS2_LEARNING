from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation (Gazebo) clock if true"
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("ros2control"),
                "urdf",
                "twowheel.urdf"
            ]),
            description="URDF file of the robot"
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "controller_config_file",
            default_value=PathJoinSubstitution([
                FindPackageShare("ros2control"),
                "config",
                "differentialdrive.yaml"
            ]),
            description="YAML file with controller configs"
        )
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_description_file = LaunchConfiguration("robot_description_file")
    controller_config_file = LaunchConfiguration("controller_config_file")

    # robot_description content (use xacro if needed)
    robot_description = {"robot_description": Command(['xacro ', robot_description_file])}

    
    # Launch Gazebo
    # -------------------------
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", "-s", "libgazebo_ros_factory.so"],
        output="screen"
    )
    
        # -------------------------
    # Spawn the Robot in Gazebo
    # -------------------------
    spawn_robot = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "twowheel_robot",
            "-file", robot_description_file,
        ],
        output="screen"
    )
    

    # robot_state_publisher node
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}, robot_description]
    )

    # controller manager (ros2_control_node)
    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        output="screen",
        parameters=[controller_config_file, robot_description]
    )

    # Spawners
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen"
    )

    differential_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["differential_controller", "--controller-manager", "/controller_manager"],
        output="screen"
    )

    return LaunchDescription(declared_arguments + [
        gazebo,
        spawn_robot,
        robot_state_publisher,
        controller_manager,
        joint_state_broadcaster_spawner,
        differential_controller_spawner
    ])
