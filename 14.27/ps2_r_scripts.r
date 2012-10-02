data = read.csv("ps2_scraped_data_2.csv", header=TRUE), sep=";")

hist(data$unit_price, main="Titleist ProV1 Golf Balls", xlab="Price Per Dozen")
dev.copy(png, 'unit_price_histogram.png')
dev.off()

