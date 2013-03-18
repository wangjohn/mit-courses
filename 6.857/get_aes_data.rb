#!/usr/bin/env ruby

9.upto(100) do |i|
  `wget http://courses.csail.mit.edu/6.857/2013/aes.php?num=9500 -O 10000_triples#{i}`
end
