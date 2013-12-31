Circuit Simulation Output Visualizer code for MIT 6.006 Fall 2011 PS2

The code distribution contains the following files:
  * bin/visualizer.html - open this in your browser to see the visualization
  * src/visualizer.erb - the HTML skeleton (uses the Erb templating language)
  * src/visualizer.scss - SCSS source for the CSS
  * src/visualizer.coffee - CoffeeScript source for the JavaScript
  * Rakefile - compiles src/* to bin/visualizer.html


BUILD

To rebuild bin/visualizer.html, you need Ruby, Rubygems, and a sane build
environment (gcc etc.). On Debian or Ubuntu, you would get this using:
    sudo apt-get install ruby rubygems ruby1.8-full build-essential
    
Then you need to install Bundler, and let it install everything else.
    sudo gem install bundler
    bundle
    
At last, use Rake (installed by Bundler) to build bin/fractal.html
    bundle exec rake
