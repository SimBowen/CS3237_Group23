import math


class MadgwickAHRS:
    """
    Implementation of Madgwick's IMU and AHRS algorithms.
    See: https://www.x-io.co.uk/node/8#open_source_ahrs_and_imu_algorithms

    Optimised for minimal arithmetic.
    Total ±: 160
    Total *: 172
    Total /: 5
    Total sqrt: 5
    """

    def __init__(self, sample_period: float, beta: float):
        self.quaternion = [1.0, 0.0, 0.0, 0.0]
        self.sample_period = sample_period
        self.beta = beta

    def update(
        self,
        gx: float,
        gy: float,
        gz: float,
        ax: float,
        ay: float,
        az: float,
        mx: float,
        my: float,
        mz: float,
    ):
        """
        Algorithm AHRS update method. Requires only gyroscope and accelerometer data.

        @param gx: Gyroscope x axis measurement in radians/s.
        @param gy: Gyroscope y axis measurement in radians/s.
        @param gz: Gyroscope z axis measurement in radians/s.
        @param ax: Accelerometer x axis measurement in any calibrated units.
        @param ay: Accelerometer y axis measurement in any calibrated units.
        @param az: Accelerometer z axis measurement in any calibrated units.
        @param mx: Magnetometer x axis measurement in any calibrated units.
        @param my: Magnetometer y axis measurement in any calibrated units.
        @param mz: Magnetometer z axis measurement in any calibrated units.
        """
        # Auxiliary variables to avoid repeated arithmetic
        q1, q2, q3, q4 = self.quaternion
        _2q1 = 2 * q1
        _2q2 = 2 * q2
        _2q3 = 2 * q3
        _2q4 = 2 * q4
        _2q1q3 = 2 * q1 * q3
        _2q3q4 = 2 * q3 * q4
        q1q1 = q1 * q1
        q1q2 = q1 * q2
        q1q3 = q1 * q3
        q1q4 = q1 * q4
        q2q2 = q2 * q2
        q2q3 = q2 * q3
        q2q4 = q2 * q4
        q3q3 = q3 * q3
        q3q4 = q3 * q4
        q4q4 = q4 * q4

        # Normalise accelerometer measurement
        norm = math.sqrt(ax * ax + ay * ay + az * az)
        if norm == 0:
            return  # handle NaN
        norm = 1 / norm  # use reciprocal for division
        ax *= norm
        ay *= norm
        az *= norm

        # Normalise magnetometer measurement
        norm = math.sqrt(mx * mx + my * my + mz * mz)
        if norm == 0:
            return  # handle NaN
        norm = 1 / norm  # use reciprocal for division
        mx *= norm
        my *= norm
        mz *= norm

        # Reference direction of Earth's magnetic field
        _2q1mx = 2 * q1 * mx
        _2q1my = 2 * q1 * my
        _2q1mz = 2 * q1 * mz
        _2q2mx = 2 * q2 * mx
        hx = (
            mx * q1q1
            - _2q1my * q4
            + _2q1mz * q3
            + mx * q2q2
            + _2q2 * my * q3
            + _2q2 * mz * q4
            - mx * q3q3
            - mx * q4q4
        )
        hy = (
            _2q1mx * q4
            + my * q1q1
            - _2q1mz * q2
            + _2q2mx * q3
            - my * q2q2
            + my * q3q3
            + _2q3 * mz * q4
            - my * q4q4
        )
        _2bx = math.sqrt(hx * hx + hy * hy)
        _2bz = (
            -_2q1mx * q3
            + _2q1my * q2
            + mz * q1q1
            + _2q2mx * q4
            - mz * q2q2
            + _2q3 * my * q4
            - mz * q3q3
            + mz * q4q4
        )
        _4bx = 2 * _2bx
        _4bz = 2 * _2bz

        # Gradient decent algorithm corrective step
        s1 = (
            -_2q3 * (2 * q2q4 - _2q1q3 - ax)
            + _2q2 * (2 * q1q2 + _2q3q4 - ay)
            - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
            + (-_2bx * q4 + _2bz * q2)
            * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
            + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
        )
        s2 = (
            _2q4 * (2 * q2q4 - _2q1q3 - ax)
            + _2q1 * (2 * q1q2 + _2q3q4 - ay)
            - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az)
            + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
            + (_2bx * q3 + _2bz * q1)
            * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
            + (_2bx * q4 - _4bz * q2)
            * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
        )
        s3 = (
            -_2q1 * (2 * q2q4 - _2q1q3 - ax)
            + _2q4 * (2 * q1q2 + _2q3q4 - ay)
            - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az)
            + (-_4bx * q3 - _2bz * q1)
            * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
            + (_2bx * q2 + _2bz * q4)
            * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
            + (_2bx * q1 - _4bz * q3)
            * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
        )
        s4 = (
            _2q2 * (2 * q2q4 - _2q1q3 - ax)
            + _2q3 * (2 * q1q2 + _2q3q4 - ay)
            + (-_4bx * q4 + _2bz * q2)
            * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx)
            + (-_2bx * q1 + _2bz * q3)
            * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my)
            + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
        )
        norm = 1 / math.sqrt(
            s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4
        )  # normalise step magnitude
        s1 *= norm
        s2 *= norm
        s3 *= norm
        s4 *= norm

        # Compute rate of change of quaternion
        qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - self.beta * s1
        qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - self.beta * s2
        qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - self.beta * s3
        qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - self.beta * s4

        # Integrate to yield quaternion
        q1 += qDot1 * self.sample_period
        q2 += qDot2 * self.sample_period
        q3 += qDot3 * self.sample_period
        q4 += qDot4 * self.sample_period
        norm = 1 / math.sqrt(
            q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4
        )  # normalise quaternion
        self.quaternion[0] = q1 * norm
        self.quaternion[1] = q2 * norm
        self.quaternion[2] = q3 * norm
        self.quaternion[3] = q4 * norm


def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)

    return roll_x, pitch_y, yaw_z  # in radians


def get_yaw(x, y, z, w):
    rad = euler_from_quaternion(x, y, z, w)[2]
    yaw = round(rad * 180 / math.pi, 2)
    return yaw
