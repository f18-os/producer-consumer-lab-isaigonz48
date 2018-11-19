# Producer Consumer Lab

* I made two files that meet the requirements because I was not sure what kind of queue we were supposed to use

## ProducerConsumer.py

* Implements a producer consumer queue to play a video

* ProConQueue (producer consumer queue) extends Queue class, but uses pcPut and pcGet instead of the regular put and get methods
  * pcPut and pcGet still call put and get respectively (Not sure if this is correct)
* Three threads to handle the three different processes of extracting, converting to grayscale, and displaying
  * Each thread has a method for its corresponding responsibility

* Used code from the given files

* Was not sure how to measure 24 fps, so I used the same frame delay as in DisplayFrames.py

* Made thread sleep for .01 seconds if they try to pcGet an empty queue, not sure if this is what was expected from the lab

## ProducerConsumerv2.py

* Mostly the same as ProducerConsumer.py except that it uses the Q class provided in the google groups instead of the queue.Queue class

* Done after I saw that post on the group and I did not know if the first version was fine or not

* Uses locks to prevent race conditions (hopefulle)