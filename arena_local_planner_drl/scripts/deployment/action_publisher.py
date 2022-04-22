#!/usr/bin/env python3
import rospy
import time

from geometry_msgs.msg import Twist
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool


# class ActionPublisher:
#     def __init__(self):
#         if rospy.get_param("train_mode"):
#             raise Exception("This node should be used solely in eval mode!")

#         rospy.init_node("action_publisher", anonymous=True)

#         self._step_size = rospy.get_param("step_size")
#         self._update_rate = rospy.get_param("update_rate")
#         # real time second in sim time
#         self._real_second_in_sim = self._step_size * self._update_rate
#         self._action_publish_rate = rospy.get_param("/robot_action_rate")

#         # apply rate in sim time
#         rate = (1 / self._action_publish_rate) / self._real_second_in_sim

#         ns_prefix = (
#             "" if "/single_env" in rospy.get_param_names() else "/eval_sim/"
#         )
#         self._pub_cmd_vel = rospy.Publisher(
#             f"{ns_prefix}cmd_vel", Twist, queue_size=1
#         )
#         self._pub_cycle_trigger = rospy.Publisher(
#             f"{ns_prefix}next_cycle", Bool, queue_size=1
#         )
#         self._sub = rospy.Subscriber(
#             f"{ns_prefix}cmd_vel_pub",
#             Twist,
#             self.callback_receive_cmd_vel,
#             queue_size=1,
#         )

#         # to measure sim time
#         # self._clock_sub = rospy.Subscriber(
#         #     f"{ns_prefix}clock", Clock, self.callback_clock)
#         # last = 0

#         self._action = Twist()
#         self._signal = Bool()
#         self._clock = Clock().clock.to_sec()

#         last_action = self._action

#         while not rospy.is_shutdown():
#             if self._sub.get_num_connections() < 1:
#                 print(
#                     f"ActionPublisher: No publisher to {ns_prefix}cmd_vel_pub yet.. "
#                 )
#                 time.sleep(1)
#                 continue

#             self._pub_cmd_vel.publish(self._action)
#             self._pub_cycle_trigger.publish(self._signal)

#             print(f"Published same action: {last_action==self._action}")
#             last_action = self._action

#             time.sleep(rate)

#             # print(f"sim time between cmd_vel: {self._clock - last}")
#             # last = self._clock

#     def callback_receive_cmd_vel(self, msg_cmd_vel: Twist):
#         self._action = msg_cmd_vel

#     def callback_clock(self, msg_clock: Clock):
#         self._clock = msg_clock.clock.to_sec()


# Action publisher with rospy.Timer
class ActionPublisher_2:
    def __init__(self):
        if rospy.get_param("train_mode"):
            raise Exception("This node should be used solely in eval mode!")

        rospy.init_node("action_publisher", anonymous=True)

        self._action_publish_rate = rospy.get_param(
            "/action_frequency", default=10
        )
        rate = rospy.Duration(
            1 / self._action_publish_rate
        )  # seconds in sim time

        self._pub_cmd_vel = rospy.Publisher("cmd_vel", Twist, queue_size=1)
        self._pub_cycle_trigger = rospy.Publisher(
            "next_cycle", Bool, queue_size=1
        )
        self._sub = rospy.Subscriber(
            "cmd_vel_pub",
            Twist,
            self.callback_receive_cmd_vel,
            queue_size=1,
        )

        self._action = Twist()
        self._signal = Bool()

        self.STAND_STILL_ACTION = Twist()
        self.STAND_STILL_ACTION.linear.x, self.STAND_STILL_ACTION.angular.z = (
            0,
            0,
        )

        self._cmd_received = False

        while self._sub.get_num_connections() < 1:
            print("ActionPublisher: No publisher to cmd_vel_pub yet.. ")
            time.sleep(1)

        rospy.Timer(rate, self.callback_publish_action)
        rospy.spin()

    def callback_publish_action(self, event):
        if self._cmd_received:
            self._pub_cmd_vel.publish(self._action)
            # reset flag
            self._cmd_received = False
        else:
            rospy.logdebug("No action received during recent action horizon.")
            self._pub_cmd_vel.publish(self.STAND_STILL_ACTION)
        self._pub_cycle_trigger.publish(self._signal)

    def callback_receive_cmd_vel(self, msg_cmd_vel: Twist):
        self._cmd_received = True
        self._action = msg_cmd_vel


if __name__ == "__main__":
    try:
        ActionPublisher_2()
    except rospy.ROSInterruptException:
        pass
