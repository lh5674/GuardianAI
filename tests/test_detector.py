import unittest

from guardianai.detector import FallDetector, PoseObservation


UPRIGHT = PoseObservation(10, 0.45, 0.48, 0.9)
HORIZONTAL = PoseObservation(75, 1.6, 0.72, 0.9)


class FallDetectorTests(unittest.TestCase):
    def test_transition_and_hold_emits_once(self):
        detector = FallDetector()
        self.assertFalse(detector.update(1, 0.0, UPRIGHT))
        self.assertFalse(detector.update(1, 0.4, HORIZONTAL))
        self.assertTrue(detector.update(1, 1.5, HORIZONTAL))
        self.assertFalse(detector.update(1, 1.6, HORIZONTAL))

    def test_lying_without_observed_transition_is_not_alert(self):
        detector = FallDetector()
        self.assertFalse(detector.update(1, 0.0, HORIZONTAL))
        self.assertFalse(detector.update(1, 2.0, HORIZONTAL))

    def test_insufficient_hip_drop_is_not_alert(self):
        detector = FallDetector()
        flat = PoseObservation(75, 1.6, 0.51, 0.9)
        detector.update(1, 0.0, UPRIGHT)
        detector.update(1, 0.2, flat)
        self.assertFalse(detector.update(1, 1.5, flat))

    def test_missing_pose_breaks_hold(self):
        detector = FallDetector()
        detector.update(1, 0.0, UPRIGHT)
        detector.update(1, 0.2, HORIZONTAL)
        detector.update(1, 0.8, None)
        self.assertFalse(detector.update(1, 1.0, HORIZONTAL))
        self.assertTrue(detector.update(1, 2.1, HORIZONTAL))

    def test_low_quality_keypoints_are_rejected(self):
        pts = [[0, 0, 0.0] for _ in range(17)]
        for index in [5, 6, 11, 12]:
            pts[index] = [10, 10, 0.9]
        pts[11][2] = 0.1
        self.assertIsNone(PoseObservation.from_keypoints(pts, [0, 0, 20, 40], 100))


if __name__ == "__main__":
    unittest.main()

