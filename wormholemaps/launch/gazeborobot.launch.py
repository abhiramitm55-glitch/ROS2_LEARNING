#launches gazebo with custom world, urdf spawner of custom robot, rosbot state publisher of custom robot


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    # --------------------------
    # Package & file paths
    # --------------------------
    pkg_name = 'wormholemaps'
    urdf_file_name = 'finalrobo.urdf'
    urdf_path = os.path.join(get_package_share_directory(pkg_name), 'urdf', urdf_file_name)
    world = os.path.join(
        get_package_share_directory('wormholemaps'),
        'worlds',
        'myhouse.world'
    )
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    # Read URDF once
    with open(urdf_path, 'r') as infp:
        robot_description = infp.read()

    # --------------------------
    # Launch Gazebo
    # --------------------------
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # --------------------------
    # Joint State Publisher
    # --------------------------
    jsp_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    # --------------------------
    # Robot State Publisher
    # --------------------------
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen'
    )

    # --------------------------
    # Spawn Robot in Gazebo
    # --------------------------
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_amr',
        arguments=['-entity', 'amr', '-file', urdf_path, '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen'
    )


    # --------------------------
    # Controller Manager
    # --------------------------
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[
            {'robot_description': robot_description},
            os.path.join(get_package_share_directory(pkg_name), 'config', 'simple_controllers.yaml')
        ],
        output='screen'
    )

    # --------------------------
    # Spawn joint_state_broadcaster
    # --------------------------
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # --------------------------
    # Spawn arm controller
    # --------------------------
    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['arm_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # --------------------------
    # LaunchDescription
    # --------------------------
    return LaunchDescription([
        gzserver_cmd,
        gzclient_cmd,
        rsp_node,
        spawn_entity,
        # controller_manager,
        # joint_state_broadcaster_spawner,
        # arm_controller_spawner
    ])
