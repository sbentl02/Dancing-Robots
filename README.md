# Dancing-Robots

This project creates a three robot waltzing group, with two leader robots and one follower robot.
The leader robots both use proportional control to line follow around a large circle while making periodic spins. They are also capable of detecting when music is playing with a machine learning algorithm to start and stop moving, or receiving a manual cue to start and stop. The follower robot uses image processing and proportional control to follow green dots placed on the rear of the leader robots. 

One leader robot starts the waltz with the follower behind, and when the leader robot reaches a red cue placed over the line, it turns away from the circle while the other leader robot on the same cue turns in to the circle, so that the second leader takes the place of the first and the follower continues by following the second. The leaders are interchangeable and can switch out repeatedly. 

All three robots use Lego SPIKE Prime hubs and corresponding Lego hardware. Each hub is also connected over serial with a Raspberry Pi, which runs the music recognition (leaders) or image processing (followers).
