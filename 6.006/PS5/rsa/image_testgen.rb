#!/usr/bin/env ruby

# Generates a random RSA key and uses it to encrypt the pixel data of an image.

require 'openssl'
require 'rubygems'
require 'RMagick'  # gem install rmagick

if ARGV.length < 2
  puts "Usage: #{$0} png_image key_size"
end

# Reads an image and breaks it into a grid of pixel RGB components.
#
# @param [String] image_path path to the image file
# @return [Array<Array<Fixnum>>] an Array with one Array for every line in the
#     image; inner arrays have RGB values for each pixel on the line
def image_pixels(image_path)
  image = Magick::Image.from_blob(File.read(image_path)).first
  sx, sy = image.columns, image.rows
  
  grid = Array.new(sy) { Array.new }
  x, y = 0, 0
  image.each_pixel do |pixel|
    grid[y].concat [pixel.red, pixel.green, pixel.blue].map { |channel|
      ((255 * channel) / Magick::QuantumRange).to_i
    }
    x += 1
    if x == sx
      x = 0
      y += 1
    end
  end
  grid
end

# Prints out a RSA key to the test input file.
#
# @param [OpenSSL::PKey::RSA] key RSA public/private key pair
def output_key(key)
  STDOUT.write "# Private key (d, n): #{'%X' % key.d} #{'%X' % key.n}\n"
  STDOUT.write "key #{'%X' % key.e} #{'%X' % key.n}\n"
end

# Prints out pixel data in an image.
#
# @param [Array<Array<Fixnum>>] pixel_array result of image_pixels() or
#                                           encrypt_image()
def output_pixel_array(pixel_array)
  pixel_array.each do |line|
    STDOUT.write "row #{line.map { |chr| '%02X' % chr}.join('')}\n"
  end
end

# Encrypts the pixel data in an image.
#
# @param [Array<Array<Fixnum>>] pixel_array result of image_pixels()
# @param [OpenSSL::PKey::RSA] key RSA public/private key pair
def encrypt_image(pixel_array, key)
  in_chunk_size = key.n.num_bytes - 1
  out_chunk_size = key.n.num_bytes

  output = []
  pixel_array.map do |in_line|
    out_line = []
    i = 0
    while i < in_line.length
      in_chunk = in_line[i, in_chunk_size].pack('C*')
      in_chunk = "\0" + in_chunk + "\0" * (in_chunk_size - in_chunk.length)
      out_chunk = key.private_encrypt in_chunk, OpenSSL::PKey::RSA::NO_PADDING
      if out_chunk.length < out_chunk_size
        out_chunk = "\0" * (out_chunk_size - out_chunk.length)
      end
      out_line.concat out_chunk.unpack('C*')
      i += in_chunk_size
    end
    out_line
  end
end


image_path = ARGV[0]
pixels = image_pixels image_path
if ARGV[1] == '2'  # hack to get a 16-bit key out of OpenSSL
  key = OpenSSL::PKey::RSA.new 1
else
  key = OpenSSL::PKey::RSA.new ARGV[1].to_i * 8
end
output_key key
STDOUT.write "sx #{pixels.first.length / 3}\n"
output_pixel_array encrypt_image(pixels, key)
STDOUT.write "end\n"
