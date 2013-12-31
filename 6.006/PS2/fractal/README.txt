Koch Snowflake Rendering code for MIT 6.006 Fall 2011 PS2

The code distribution contains the following files:
  * bin/fractal.html - open this in your browser to see the fractal
  * src/fractal.erb - the HTML skeleton (uses the Erb templating language)
  * src/fractal.scss - SCSS source for the CSS
  * src/fractal.coffee - CoffeeScript source for the JavaScript
  * src/raphael.js - a JavaScript library for rendering to SVG
  * Rakefile - compiles src/* to bin/fractal.html


BUILD

To rebuild bin/fractal.html, you need Ruby, Rubygems, and a sane build
environment (gcc etc.). On Debian or Ubuntu, you would get this using:
    sudo apt-get install ruby rubygems ruby1.8-full build-essential
    
Then you need to install Bundler, and let it install everything else.
    sudo gem install bundler
    bundle
    
At last, use Rake (installed by Bundler) to build bin/fractal.html
    bundle exec rake
