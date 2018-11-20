# Producer Consumer Lab

## ProducerConsumer.py

* Implements a producer consumer queue to play a video

* ProConQueue (producer consumer queue) extends Q class, which was given in the google group
  * pcPut and pcGet still call put and get respectively
  * pcPut and pcGet use semaphores to implement the producer consumer queue
  
* Three threads to handle the three different processes of extracting, converting to grayscale, and displaying
  * Each thread has a method for its corresponding responsibility
  * They all use ProConQueue that is given to them

* Used code from the given files

* Was not sure how to measure 24 fps, so I used the same frame delay as in DisplayFrames.py