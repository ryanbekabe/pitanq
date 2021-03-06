import unittest
import time
import warnings
import os
import logging

import cv2 as cv

import MotorCtrl
import DistCtrl
import PhotoCtrl
import HaarDetectCtrl
import DnnDetectCtrl
import ClassifyCtrl
import FollowLineCtrl
import WalkCtrl

import track_cv


class MotorTest(unittest.TestCase):

    motor_ctrl = MotorCtrl.createMotorCtrl()

    def test_fwd(self):
        self.motor_ctrl.fwd_on()
        self.motor_ctrl.fwd_off()

    def test_back(self):
        self.motor_ctrl.back_on()
        self.motor_ctrl.back_off()

    def test_right(self):
        self.motor_ctrl.right_on()
        self.motor_ctrl.right_off()

    def test_left(self):
        self.motor_ctrl.left_on()
        self.motor_ctrl.left_off()


class DistanceTest(unittest.TestCase):

    dist_ctrl = DistCtrl.createDistCtrl()

    def test_dist(self):
        d = self.dist_ctrl.distance()
        if d < 0:
            warnings.warn(("Probably distance meter does not work properly", d))

class PhotoTest(unittest.TestCase):

    photo_ctrl = PhotoCtrl.createPhotoCtrl()

    def test_photo(self):
        rc, phid = self.photo_ctrl.make_photo()
        self.assertEqual(rc, True, "Photo failed")
        self.assertEqual(phid is not None, True, "Photo id is none")
        path, fname = self.photo_ctrl.get_path(phid)
        self.assertEqual(path is not None, True, "Photo path is none")
        fpath = path + "/" + fname
        self.assertEqual(os.path.exists(fpath), True, "Photo file does not exist: " + fpath)
        self.assertEqual(os.path.getsize(fpath) > 0, True, "Photo file is empty")
        os.remove(fpath)

class HaarTest(unittest.TestCase):

    haar = HaarDetectCtrl.createDetectCtrl()

    def test_cat(self):
        path_cat = "/home/pi/pitanq/test/data/cat.jpg"
        rc = self.haar.detect_file(path_cat)
        self.assertEqual(rc is not None, True, "Cat not found")


class DnnDetectTest(unittest.TestCase):

    dnn = DnnDetectCtrl.createDetectCtrl()

    def test_detect(self):
        path = "/home/pi/pitanq/test/data/detect.jpg"
        rc = self.dnn.detect_file(path)
        self.assertEqual(rc is not None, True, "Nothing detected by DNN")
        cat_found = False
        laptop_found = False
        for r in rc:
            name = r["name"]
            if name == "cat":
                cat_found = True
            elif name == "laptop":
                laptop_found = True
        self.assertEqual(cat_found, True, "Cat not detected by DNN")
        self.assertEqual(laptop_found, True, "Laptop not detected by DNN")


class TFClassifyTest(unittest.TestCase):

    cls = ClassifyCtrl.createClassifyCtrl()

    def test_detect(self):
        path = "/home/pi/pitanq/test/data/detect.jpg"
        rc = self.cls.classify_ex(path)
        self.assertEqual(rc is not None, True, "Nothing detected by TF")
        laptop_found = False
        for r in rc:
            name = r["item"]
            if name.find("laptop") != -1:
                laptop_found = True
        self.assertEqual(laptop_found, True, "Laptop not detected by TF")

class MockPhotoCtrl:
    path = None
    name = None

    def init(self, path, name):
        self.path = path
        self.name = name

    def make_photo(self):
        return True, self.name
        

    def get_path(self, phid):
        return self.path, phid + ".jpg"


class MockMotorCtrl:


    def fwd_on(self):
        return True

    def fwd_off(self):
        return True

    def back_on(self):
        return True

    def back_off(self):
        return True

    def right_on(self):
        return True

    def right_off(self):
        return True

    def left_on(self):
        return True

    def left_off(self):
        return True


class FollowTest(unittest.TestCase):

    def test_vector(self):
        path = "/home/pi/pitanq/test/data/follow.jpg"
        angle, shift = track_cv.handle_pic(path)
        self.assertEqual(angle is not None, True, "Angle not found")
        self.assertEqual(int(angle) == 90, True, "Invalid angle: "  + str(angle))

    def test_prepare(self):
        m = MockMotorCtrl()
        ph = MockPhotoCtrl()
        follow = FollowLineCtrl.FollowLineCtrl(m, ph)
        ph.init("/home/pi/pitanq/test/data", "follow")

        angle, shift = follow.prepare_follow()
        print("Prepare", angle, shift)

class WalkTest(unittest.TestCase):

    def test_classify(self):
        m = MockMotorCtrl()
        ph = MockPhotoCtrl()
        w = WalkCtrl.WalkCtrl(m, ph)
        ph.init("/home/pi/pitanq/test/data", "nns")

        w.avg = 130
        s_path = "test/data/nns.jpg"    
        w.last_s_path = s_path

        img = cv.imread(s_path)
        g_path = "test/data/g_nn.jpg"    
        a = w.handle_small(img, g_path)
        self.assertEqual(a == -1, True, "Incorrect prediction:" + str(a))


    def test_classify_ex(self):
        m = MockMotorCtrl()
        ph = MockPhotoCtrl()
        w = WalkCtrl.WalkCtrl(m, ph)
        ph.init("/home/pi/pitanq/test/data", "nn")
        rc = w.prepare_action()
        self.assertEqual(rc, True, "Walk prepare failed")

        
        


if __name__ == '__main__':
    log_file = "/home/pi/local_test.log"
    logging.basicConfig(filename=log_file,level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(threadName)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    unittest.main()
