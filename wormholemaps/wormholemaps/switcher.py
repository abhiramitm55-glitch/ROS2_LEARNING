import sys
import rclpy
from rclpy.node import Node
from nav2_msgs.srv import LoadMap
from geometry_msgs.msg import PoseWithCovarianceStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

map=[ 
    "/home/abhirami/wormhole/src/wormholemaps/map/map1.yaml",
    "/home/abhirami/wormhole/src/wormholemaps/map/map2.yaml"
]




class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(LoadMap,'/map_server/load_map')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = LoadMap.Request()
        self.req.map_url = map[0]
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=10
        )
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,  # Message type
            '/amcl_pose',               # Topic name
            self.listener_callback,     # Callback
            qos
        )
        self.subscription 

    def send_request(self,map_url):
        #comparing values between curret map and the future map
        if not self.req.map_url == map_url:


            self.req.map_url= map_url
            
            future=self.cli.call_async(self.req)
            future.add_done_callback(self.my_callback)


    def my_callback(self,future):
        try:
            response=future.result()
            self.get_logger().debug(f"Map load response: {response}")
        except Exception as e:
            self.get_logger().error(f"Service call failed: {e}")
    


    def listener_callback(self, msg):
        pose = msg.pose.pose
        x = pose.position.x
        y = pose.position.y
        z = pose.position.z  # usually 0 for ground robots
        self.get_logger().debug(f"Robot Pose -> x: {x:.2f}, y: {y:.2f}, z: {z:.2f}")
        if x > 3 :
            #switch map


            future=self.send_request(map[0])


        elif x <= 3:
            #switch to initial map

            future=self.send_request(map[1])

def main():
    rclpy.init()

    minimal_client = MinimalClientAsync()
    # minimal_client.get_logger().info(
    #     'Result ')
    rclpy.spin(minimal_client)
    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
