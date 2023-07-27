## Get the climate data --------------------------------------------------------
# This function implements 'clifro' package to retrive historical climate data 
# in NIWA's database in New Zealand.

library(dplyr)
library(lubridate)
library(clifro) 

# Set up user account (This must be done on NIWA's website!)
cur.user <- cf_user('saeed@landwatersci.net', 'UNR5KGBO')

get_climate_data <- function(id, d.type, where, date) {
  tryCatch({
    # Create a lookup table for data types
    data.type.lookup <- list(
      wind = cf_datatype(2, 1, 2, 1),
      rain = cf_datatype(3, 1, 1),
      air.temp = cf_datatype(4, 2, 1),
      earth.temp = cf_datatype(4, 3, c(1, 2, 3, 4, 5)),
      soil.moist = cf_datatype(9, 2, 1)
    )
    
    # Use the lookup table to get the data type
    data.type <- data.type.lookup[[d.type]]
    
  }, error = function(e) {
    stop('We encountered an error when trying to find the data type  ',
         d.type, '\n Please see below:\n', conditionMessage(e))
    NULL
  })
  
  tryCatch({
    # Search all weather stations within the vicinity of the requested location
    stations.list.location <- cf_find_station(lat = where[1], long = where[2], rad = where[3], search = 'latlong')
    
    # Sort the list based on their distance from the requested location
    stations.list <- stations.list.location[order(stations.list.location$distance), ]
    
    # Extract the stations detailes
    station.data <- data.frame(
      Station = stations.list$name,
      distance = stations.list$distance
    )
    
    # Check if the list of stations is empty
    if (nrow(stations.list) < 1) {
      stop('There is no station within the ', where[3], 'km of your requested location.',
           '\n Please try another location or increase the radius')
    } else {
      dat <- data.frame()
      ## Define the number of rows in each smaller list of stations
      rows.per.list <- 10
      
      ## Calculate the number of smaller lists
      num.lists <- ceiling(nrow(stations.list) / rows.per.list)
      
      #' Split the stations list into smaller lists with 10 stations at max.
      #' This is because of the limitation set by the package
      smaller.st.lists <- lapply(seq_len(num.lists), function(i) {
        start.row <- (i - 1) * rows.per.list + 1
        end.row <- min(i * rows.per.list, nrow(stations.list))
        stations.list[start.row:end.row, ]
      })
    }
    
  }, error = function(e) {
    stop('We encountered an error when trying to find stations within the ',
         where[3], ' km of your requested location!',
         '\n Please see below:\n', conditionMessage(e))
    NULL
  }, warning = function(w) {
    # Warning handler
    warning("A warning occurred: ", conditionMessage(w))
    NULL
  })
  
  #' Loop through the list that contains the list of stations and make inquries
  #' from NIWA's CliFlo' database
  dat <- data.frame()
  for (inquired.stations in smaller.st.lists) {
    tryCatch({
      # Make a batch inquiry from NIWA's CliFlo' database
      query <- cf_query(
        user = cur.user,
        datatype = data.type,
        station = inquired.stations,
        start_date = paste(date[1], '00'), # e.g., "2017-01-01 00"
        end_date = paste(date[2], '00')
      )
      
      # Convert the results into a data frame and combine them
      dat <- rbind(dat, as.data.frame(query))
      
      # If the climate data exsist for the requested set of stations stop the sereach
      if (nrow(dat) > 0) {
        break
      }
      
      # # Save the retrived climate data in a csv
      # file_name <- paste("Report/", id, "_", date[2], "_", d.type, ".csv", sep = "")
      # file_dir <- paste(out.f.dir, file_name, sep = "")
      # 
      # # Save the data.frame to a CSV file with the constructed file name
      # write.csv(dat, file = file_dir, row.names = FALSE)
      
    }, error = function(e) {
      # Return a value indicating the error condition (optional)
      return(NA)
    })
  }
  
  tryCatch({
    # Select only the numeric columns
    numeric.cols <- sapply(dat, is.numeric)
    numeric.dat <- dat[c("Station", names(dat)[numeric.cols])]
    
    # Calculate the mean of numeric columns based on unique values of "Station"
    dat.mean <- numeric.dat %>%
      group_by(Station) %>%
      summarise(across(everything(), mean))
    
    # Add the distance attribute of stations to the final result
    dat.mean <- left_join(as.data.frame(dat.mean), station.data, by = c("Station" = "Station")) %>%
      arrange(distance)
  }, error = function(e) {
    # Return a value indicating the error condition (optional)
    return(NA)
  })
  
  message("Search for the climate data for the requested stations completed")
  return(as.data.frame(dat.mean))
  # return(list(result1 = as.data.frame(dat.mean), result2 = station.data))
}

## Calculate mean IDW value ----------------------------------------------------
# This function calculate the mean IDW value of climate data based on the 
# distance of the weather station from the requested location
get_idw_mean <- function(data, distance.col, d.type, power = 2) {
  tryCatch({
    # Create a lookup table for the parameter names
    parameter.lookup <- list(
      wind = "Speed.m.s.",
      rain = "Amount.mm.",
      air.temp = "Tmean.C.",
      earth.temp = "Tearth.C.",
      soil.moist = "Percent..."
    )
    # Use the lookup table to get the parameter name
    value.col <- parameter.lookup[[d.type]]
    
    # Calculate the weights as the inverse of distance raised to the power
    data$weight <- 1 / (data[[distance.col]]^power)
    
    # Calculate the weighted sum
    weighted.sum <- sum(data[[value.col]] * data$weight)
    
    # Calculate the sum of weights
    sum.weights <- sum(data$weight)
    
    # Calculate the IDW mean
    idw.mean <- weighted.sum / sum.weights
    
    return(idw.mean)
  }, error = function(e) {
    # Return a value indicating the error condition (optional)
    return(NA)
  })
}

## Get the sampling site locations and dates -----------------------------------
library(dplyr)
library(reticulate)
library(lubridate)
library(tidyr)

# Assign the data directory
out.f.dir = "C:/Users/SaeedR/Desktop/Saeed/App/Data/Climate/"

# Set the file path for the .p (pickle) file
in.f.dir <- 'C:/Users/SaeedR/Desktop/Saeed/App/Data/WQ_Data_Nov2021.p'

# Use reticulate to read the pickle data
dat.dic <- py_load_object(in.f.dir)

# Prepare the sampling dataset
stackframe <- dat.dic$StackFrame
metadata <- dat.dic$metadataWQ
metadata <- subset(metadata, select = -geometry)

# Filter the sampling dataset to contain only 2019 and later.
filtered.stackframe <- stackframe %>%
  filter(Year > 2018)
filtered.metadata <- metadata %>%
  filter(nzsegment %in% filtered.stackframe$nzsegment)

# Create a lookup table for the parameter names
climate.parameters <- c("rain", "air.temp", "earth.temp", "soil.moist") # "wind",

# Create an empty list that will contain all the climate data for all sampling 
# sites over the sampling periods
climate.dat.list <- list()

# Loop over the sampling sites list
# for (i in 1:nrow(filtered.metadata[1:2, ])) {
for (i in 1:nrow(filtered.metadata)) {
  seg.id <- filtered.metadata$nzsegment[i]
  lat <- filtered.metadata$lat[i]
  lon <- filtered.metadata$long[i]
  
  cat(i, "We are collecting data for sampling site", seg.id, "\n")
  
  # Get the sampling dates for the current sampling site
  sampeling.dates <- filtered.stackframe$myDate[filtered.stackframe$nzsegment == seg.id] %>%
    unique()
  
  # Convert the list to a vector
  date_vector <- sapply(sampeling.dates, as.character)
  
  # Get the unique values
  sampeling.dates <- unique(date_vector)

  # Create an empty data frame that will contain all the climate data for a
  # specific sampling site over all sampling periods
  # Create an empty dataframe to store the results for this ID
  seg.climate.dat <- data.frame(SegID = character(), Date = character(), Parameter = character(), Val = numeric())

  # Loop over the sampling dates for the current sampling site
  # for (date in sampeling.dates[1:2]) {
  for (date in sampeling.dates) {
    # reformat the sampling date to string
    end.date <- date #format(date, "%Y-%m-%d")

    # Subtract 1 day from the sampling date
    start.date <- as.Date(end.date) - 1

    # Loop over the list of climate data
    # for (data.type in climate.parameters[1:2]) {
    for (data.type in climate.parameters) {
      # Request the historical climate data from NIWA
      climate.dat <- get_climate_data(seg.id, data.type, c(lat, lon, 100), 
                                      c(start.date, end.date))
      
      # Save the retrived climate data in a csv
      file_name <- paste("Processed/", i, "_", seg.id, "_", date, "_", data.type, ".csv", sep = "")
      file_dir <- paste(out.f.dir, file_name, sep = "")
      
      # Save the data.frame to a CSV file with the constructed file name
      write.csv(climate.dat, file = file_dir, row.names = FALSE)
      
      # Call the function to calculate the IDW mean of the "Percent..." column
      idw.mean.val <- get_idw_mean(data=climate.dat, distance.col="distance", 
                                   d.type=data.type)

      # Store the result in the dataframe
      seg.climate.dat <- rbind(seg.climate.dat, data.frame(SegID = seg.id, 
                                                           Date = end.date,
                                                           Parameter = data.type,
                                                           Val = idw.mean.val))
    }
  }
  # Append the results for the current sampling site into the climate data list
  climate.dat.list[[seg.id]] <- seg.climate.dat
}

# Create a data frame that contains all the climate data for all sampling sites
# over the sampling periods
climate.dat <- do.call(rbind, climate.dat.list)
climate.dat <- pivot_wider(climate.dat, names_from = Parameter, values_from = Val)
