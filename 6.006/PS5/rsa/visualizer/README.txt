Image Decryption result visualizer for MIT 6.006 Fall 2011 PS5

The code distribution contains the following files:
  * bin/visualizer.html - open this in your browser to see the visualization
  * dev/server.rb - development server that re-compiles src/* on every reload
  * src/visualizer.erb - the HTML skeleton (uses the Erb templating language)
  * src/visualizer.scss - SCSS source for the CSS
  * src/visualizer.coffee - CoffeeScript source for the JavaScript
  * Rakefile - compiles src/* to bin/visualizer.html
  * Gemfile, Gemfile.lock - bundler manifest with the required gem versions


BUILD

To rebuild bin/visualizer.html, you need Ruby, Rubygems, and a sane build
environment (gcc etc.). On Debian or Ubuntu, you would get this using:
    sudo apt-get install ruby rubygems ruby1.9.1-full build-essential
    
Then you need to install Bundler, and let it install everything else.
    sudo gem install bundler
    bundle
    
At last, use Rake (installed by Bundler) to build bin/visualizer.html
    bundle exec rake

While modifying the source code, you should launch a dev server that will
recompile the code on every browser refresh.
    rake server
