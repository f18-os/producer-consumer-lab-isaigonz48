# Producer Consumer Lab

* Implements a producer consumer queue to play a video

* ProConQueue (producer consumer queue) extends Queue class, but uses pcPut and pcGet instead of the regular put and get methods

* Three threads to handle the three different processes of extracting, converting to grayscale, and displaying

** Each thread has a method for its corresponding responsibility

* Used code from the given files

* Was not sure how to measure 24 fps, so I used the same frame delay as in DisplayFrames.py

* Made thread sleep for .1 seconds if they try to pcGet an empty queue, not sure if this is what was expected from the lab