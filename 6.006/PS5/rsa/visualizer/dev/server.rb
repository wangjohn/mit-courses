#!/usr/bin/env ruby
require 'bundler/setup'
require 'sinatra'

require 'erubis'
require 'sass'
require 'coffee-script'

# Serve files in public without any modification.
set :public_folder, File.join(File.dirname(__FILE__), 'public')

# Serve templates from src/
set :views, File.expand_path('../src', File.dirname(__FILE__))

helpers do
end

get '/' do
  erb :"visualizer.html"
end

get '/:name.jsonp' do
  File.read File.expand_path("../../#{params[:name]}.jsonp",
                             File.dirname(__FILE__))
end
