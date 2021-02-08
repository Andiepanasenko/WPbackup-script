require "bundler/setup"
Bundler.require(:default)
require 'sinatra'
require 'resque/server'
require 'resque/scheduler'
require 'resque/scheduler/server'
require 'yaml'

Resque.redis = Redis.new

# Or, with custom options
 Resque.redis = Redis.new({
   :host => "dev-denise.d5xhkl.0001.use1.cache.amazonaws.com",
   :port => 6379,
   :db => DB_NUM,
 })

Resque.redis.namespace = 'DEV_NUM'

run Rack::URLMap.new \
  "/DEV_NUM/resque" => Resque::Server.new

