# Setup -------------------------------------------------------------------
## Load the dplyr package
library(dplyr)

## Install, update, and load the clifro package
install.packages('remotes')
remotes::install_github('ropensci/clifro')
library(clifro) 
packageVersion('clifro') # 3.2.5.9000
help(package = clifro)
help(cf_find_station, package='clifro')

## Set up user account (This must be done on NIWA's website!)
cur.user <- cf_user('saeed@landwatersci.net', 'UNR5KGBO')


# Find_Sation_Function ----------------------------------------------------

#' This function implements 'clifro' package to find weather stations in
#' New Zealand. #' The functions is based on the three following
#' search/filtering criteria:
#'    1) Location: it search for all stations in the vicinity of a location
#'    2) Time: it filters all the nearby stations that were active during a
#'      time-period
#'    3) Data Type: it filters out the selected stations, if they don't collect
#'      a data type (e.g., wind) 
#'
#' @param dates A numeric vector that contains Start and End date
#' @param data.type An object of class 'cfdatatype' in 'clifro' package that
#'                  contains the requested data types. Note: this object may
#'                  specify one or several datatype. The function search for
#'                  stations that measure all those data types.
#' @param where A numeric vector that contains X, Y, and Radius(Km) of the
#'              requested location. The X and Y must be given in decimal degrees.
#' @return A 'cfStation' object that contains a list of stations that meet all
#'         the above criteria.
get_stations_list <- function(dates, data.type, where) {
  # Search based on location ------------------------------------------------
  result <- tryCatch({
    ## Search all weather stations within the vicinity of the requested location
    stations.list1 <- cf_find_station(lat=where[1], long=where[2],
                                      rad=where[3], search='latlong')
    ## Sort the list based on their distance from the requested location
    stations.list1 = stations.list1[order(stations.list1$distance), ]
    
    ## Check if the list of stations is empty
    if (nrow(stations.list1) < 1){
      stop('There is no station in the vicinity of your requested location.',
           '\n Please try another location or increase the radius')
    }
  }, error = function(e) { 
    message('We encountered an error when trying to find stations in the
            vicinity of your requested location! Here is the error:\n')
    print(e)
  })
  
  # Search based on dates --------------------------------------------------
  ## Filter the results of the previous search with the dates
  result <- tryCatch({
    ## Read the user input start and end dates
    start.date <- as.Date(dates[1], format='%Y-%m-%d')
    end.date <- as.Date(dates[2], format='%Y-%m-%d')
    
    #' Search (one-by-one) if the stations in the list were operating during
    #' the requested time period. This is do to limitation of the 'clifro' package.
    temp <- list()
    ## Note: the number is limited to the first 100 stations to increase the speed
    if (nrow(stations.list1) > 100){n=100} else {n=nrow(stations.list1)}
    for (i in 1:n){
      if (stations.list1[i, 4] < start.date &&
          stations.list1[i, 5] > end.date){
            #' Add the 'Agent Id' of the satiation to a list if it meets the time
            #' criteria
            temp <- c(temp, stations.list1[i, 3])
      }
    }
    
    ## Check if the list of stations is empty
    if (length(temp) < 1){
      stop('There is no station in the vicinity of your requested location that
           has measured data during your requested time', '\n Please check your
           requested time period or try another input')
    }
    
    #' Create a cfStation object (it only works with 'Agent ID') that contain the
    #' list of stations
    stations.list2 = cf_station(temp)
    rm(temp)
    
  }, error = function(e) { 
    message('We encountered an error while trying to filter the stations with
            your requested time period')
    print(e)
  })


  # Search based on data type -----------------------------------------------
  ## Filter the results of the previous search with the data_types
  temp <- list()
  for (i in 1:nrow(stations.list2[1:5])){
    result <- tryCatch({
      #' Add the 'Agent Id' of the satiation to a list if it meets the data type
      #' criterion. If the criterion is not met, 'tryCatch' operation disregards
      #' the station and moves to the next station
      temp.stations.list2 <- cf_find_station(stations.list2[i, 2],
                                            search = "network",
                                            datatype = data.type,
                                            status='all')
      temp <- c(temp, stations.list2[i, 3])
      
    }, error = function(e){ 
      # message(stations.list2[i, 1], 'does not measure your requested data type')
      # print(e)
    })
  }
  
  ## Check if the list of stations is empty
  if (length(temp) < 1){
    stop('There is no station in the vicinity of your requested location that has
       measured your requested data type. Please check your requested data type
       and try again')
  }
  stations.list3 <- cf_station(temp)
  rm(temp)

  # Prepare the results -----------------------------------------------------
  ## Add the distance attribute of stations to the final result
  match_idx <- match(stations.list3$agent, stations.list1$agent, nomatch = 0)
  stations.list3$distance <- stations.list1$distance[match_idx]
  stations.list3 <- stations.list3[order(stations.list3$distance), ]
  
  ## Give a message to users about the results
  message('There are ', nrow(stations.list1), ' satations whithin ',
          where[3], ' killometers of your requested location (', where[1],
          ', ', where[2], '), ', nrow(stations.list2),
          ' of which measure(d) your requested data type. Out of these ',
          nrow(stations.list3),
          ' stations have collected data during your requested time period')
  rm(stations.list1, stations.list2)
  return(stations.list3)
}


# Get the climate report --------------------------------------------------
#' This function gets the historical weather reports from NIWA 'clifro' package 
#'
#' @param dates A numeric vector that contains Start and End date
#' @param data.type An object of class 'cfdatatype' in 'clifro' package that
#'                  contains the requested data types. Note: this object may
#'                  specify one or several datatype. The function search for
#'                  stations that measure all those data types.
#' @param stations.list An object of class 'cfstation' in 'clifro' package that
#'                 contains the a list of Stations
#' @return A dataframe object that contains weather reports of the requested data
#'         type(s) during the specified period, measured in the requested stations 
get_climate_date <- function(dates, data.type, stations.list) {
  result = tryCatch({
    ## Make an inqurey from NIWA's CliFlo' database
    query <- cf_query(user = cur.user,
                      datatype = data.type,
                      station = stations.list,
                      start_date = paste(date[1], '00'), # e.g., "2017-01-01 00"
                      end_date = paste(date[2], '00')) # e.g., "2017-02-01 00"
    ## Convert the results into a data frame
    dat <- as.data.frame(query)
    
    return(dat)
  }, error = function(e) { 
    message('We encountered an error while trying to acquire the report with
            your specific inquery (time, data type, and stations). Please see the
            error below: \n')
    print(e)
  })
}


# Calculate the weighted mean of a variable -------------------------------
#' This function calculates the weighted mean of a climate variable (e.g., air
#' temperature) based on the inverse distance weight method.
#' 
#' @param measured.df A data frame that contains the measure variable in one or
#'                    several stations during a period of time.
#' @param stations.list An object of class 'cfstation' in 'clifro' package that
#'                      contains the a list of Stations, where the variable has
#'                      been measured.
#' @return A single numeric value  
calc_weighted_mean <- function(measured.df, stations.list) {
  result = tryCatch({
    ## Get the stations distances to the requested location in a vector
    stations.list$distance <- ifelse(stations.list$distance == 0, 0.1,
                                     stations.list$distance)
    stations.distances <- c(stations.list$distance)
    
    # set the power parameter
    p <- 2
    
    # calculate the weights
    stations.weights <- (1/(stations.distances ^ p))/sum((1/(stations.distances ^ p)))
    
    
    # group by the "group" column and get the mean of the "value" column
    ave.stations <- measured.df %>%
      group_by(Station) %>%
      summarise(mean_value = mean(target_var))
    
    
    # calculate the weighted mean
    weighted_mean <- sum(stations.weights * ave.stations$mean_value)
    
    return(weighted_mean)
  }, error = function(e) { 
    message('We encountered an error while trying to calculate the weighted mean
            of ', target_var, '. Please see the error bellow: \n')
    print(e)
  })
}


# Assign_Variables --------------------------------------------------------
## Assign the Start and End Dates
date = c('2017-01-01', '2017-01-11')

## Assign the search location and the radius
location = c(-35.13352, 173.26294, 20)

#' Specify the data types (Note these values are from the clifro website, where you can
#' manually search for climate data: https://cliflo.niwa.co.nz/pls/niwp/wgenf.genform1_proc).
#' For example, 'daily.earth.temp.dt' specifies the temperature (4) of earth (3) in 10cm (2),
#' and 50cm (5) depth
daily.wind.dt = cf_datatype(2, 2, 1, 1)
daily.rain.dt = cf_datatype(3, 1, 1)
daily.air.temp.dt = cf_datatype(4, 2, 1)
daily.earth.temp.dt = cf_datatype(4, 3, c(2, 5))
daily.soil.moist.dt = cf_datatype(9, 2, 1)

## Combine all data types into one object
daily.combined.dt <- cf_datatype(select_1 = c(2,3,4,4,9),
                                 select_2 = c(2,1,2,3,2),
                                 check_box = list(1,1,1,c(2, 5),1),
                                 combo_box = c(1,NA,NA,NA,NA))


# Get the stations lists for specific time, location, and data.types
wind.stations.list = get_stations_list(date, daily.wind.dt, location)
rain.stations.list = get_stations_list(date, daily.rain.dt, location)
air.temp.stations.list = get_stations_list(date, daily.air.temp.dt, location)
earth.temp.stations.list = get_stations_list(date, daily.earth.temp.dt, location)
soil.moist.stations.list = get_stations_list(date, daily.soil.moist.dt, location)


if (nrow(rain.stations.list) > 0){
  dat <- get_climate_date(dates, daily.rain.dt, rain.stations.list)
}
    
if (nrow(dat) > 0){
  colnames(dat)[colnames(dat) == "Amount.mm."] <- "target_var"
  mean.val <- calc_weighted_mean(dat, rain.stations.list)
}


# Extras ------------------------------------------------------------------

## This section breaks down the list into several smaller lists.
## This because the find_station function only accepts 20 stations,
## when trying to filter the stations with the data_type.
# temp.list = list()
# len = nrow(stations.list1)
# if (len > 20){
#   for (i in 1:ceiling(len/20)){
#     s = ((i-1)*20)+1
#     e = ((i-1)*20)+20
#     if (e > len){e=len}
#     temp.list[[i]] <- list(stations.list1[s:e])
#     # temp.list <- c(temp.list, stations.list1[s:e])
#   } 
# } else {
#   temp.list <- stations.list1
# }