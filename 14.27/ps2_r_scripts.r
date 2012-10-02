#data = read.csv("ps2_scraped_data_2.csv", header=TRUE, sep=";")
#
#hist(data$unit_price, main="Titleist ProV1 Golf Balls", xlab="Price Per Dozen")
#dev.copy(png, 'unit_price_histogram.png')
#dev.off()

data = read.csv("ps2_scraped_data_3.csv", header=TRUE, sep=";")
data$was_sold = as.numeric(data$was_sold)-1
final_buyer_data = data[data$final_buyer=='True',] 

# regressions to see how price varies with buyer reputation
result_base = glm(unit_price ~ buyer_score + seller_score, data=final_buyer_data)
result_2 = glm(unit_price ~ buyer_score + seller_score + percentage_capitals + number_annoying_punctuation, data=final_buyer_data)

# regressions to see how these variables affect how close you were to the actual sale price
data$distance_to_final_price = data$price - data$price_of_bid
result_3 = glm(distance_to_final_price ~ buyer_score + seller_score, data=data)

summary(result_base)
summary(result_2)
summary(result_3)

    
