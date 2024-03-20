import os, yaml
import rospy, rospkg, tf2_ros
from tf2_msgs.srv import FrameGraph

import tf.transformations as tfs

import time, math

from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QDialog, QTextEdit

class GTDialog(QDialog):

    def __init__(self):
        super(GTDialog, self).__init__()

        rp = rospkg.RosPack()
        ui_file = os.path.join(rp.get_path('rqt_bag'), 'resource', 'gt_widget.ui')
        loadUi(ui_file, self)

        # self.result.setReadOnly(True)

        self.get_button.setText('Get GT')
        self.get_button.clicked[bool].connect(self._handle_gt_clicked)
        
        self.quat_text = QTextEdit()
        self.quat_text.setReadOnly(True)
        self.quat_text.setLineWrapMode(QTextEdit.NoWrap)

        self.euler_text = QTextEdit()
        self.euler_text.setReadOnly(True)
        self.euler_text.setLineWrapMode(QTextEdit.NoWrap)

        self.result_tab.addTab(self.quat_text, "Quat")
        self.result_tab.addTab(self.euler_text, "Euler")

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)      

        time.sleep(0.2)
        self._update_box()

    def _update_box(self):
        rospy.wait_for_service('~tf2_frames')
        tf2_frame_srv = rospy.ServiceProxy('~tf2_frames', FrameGraph)
        yaml_data = tf2_frame_srv().frame_yaml
        data = yaml.safe_load(yaml_data)
        self.tf_frames = data.keys()

        for e in self.tf_frames:
            self.parent_box.addItem(e)
            self.child_box.addItem(e)

    def _handle_gt_clicked(self):
        
        pn = self.parent_box.currentText()
        cn = self.child_box.currentText()

        print('parent: {}, child: {}'.format(pn, cn))

        trans = self.tf_buffer.lookup_transform(pn, cn, rospy.Time(0))
        
        # print(tfs)
        
        q = trans.transform.rotation
        t = trans.transform.translation

        quat_text = 'rot:\t[{:.6f}, {:.6f}, {:.6f}, {:.6f}]\n\ntrans(m):\t[{:.6f}, {:.6f}, {:.6f}]'.format(q.x, q.y, q.z, q.w, t.x, t.y, t.z)

        self.quat_text.setText(quat_text)

        el_r = tfs.euler_from_quaternion([q.x, q.y, q.z, q.w])
        el_d = [180.0 / math.pi * x for x in el_r]

        euler_text = 'rpy(rad):\t[{:.6f}, {:.6f}, {:.6f}]\n\nrpy(deg):\t[{:.6f}, {:.6f}, {:.6f}]\n\ntrans(m):\t[{:.6f}, {:.6f}, {:.6f}]'.format(
                el_r[0], el_r[1], el_r[2], el_d[0], el_d[1], el_d[2], t.x, t.y, t.z)

        self.euler_text.setText(euler_text)