library(patchwork)
library(fastDummies)
library(tidyverse)
library(modelsummary)
library(dplyr)
library(knitr)
library(ggplot2)
library(did)
library(plm)
library(openxlsx)
library(tableone)
library(extrafont)
library(kableExtra)


#2018
morg08 <- read_csv("data/csv/morg08.csv")
public08 <- morg08 |> 
  filter(class94 %in% c( 1,2,3))
#private, self employed, or without pay, 
#is class94 = 4, 5,6, 7, and 8 so exclude those. 
#Also excludes NAs
#32,403 entries now, was 317,341

public08$young <- ifelse(public08$age <= 30, 1, 0) 
#this creates a new col, "young" and its 1 if age is equal to or less than 30

sum(public08$young == 1) #5563 observations of young out of 32,403

sum(public08$weight[public08$young == 1]) #summing weights now 
#12579384

sum(public08$weight) #68065402
12579384/68065402 *100 #18.48132 

View(public08)

public08IL <- morg08 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public08IL$young <- ifelse(public08IL$age <= 30, 1, 0)

sum(public08IL$young == 1) #147 out of 849 obs 
(147/849)*100 #17.31449 #unweighted

sum(public08IL$weight[public08IL$young == 1]) #summing weights now 
#494082

sum(public08IL$weight) #2607100
494082/2607100 *100 #18.9514 

((sum(public08IL$weight[public08IL$young == 1]))/(sum(public08IL$weight)))*100 #18.9514

View(public08IL) #can use this to check number of obs

public08NY <- morg08 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public08NY$young <- ifelse(public08NY$age <= 30, 1, 0) 

((sum(public08NY$weight[public08NY$young == 1]))/(sum(public08NY$weight)))*100 #18.88321

sum(public08NY$young == 1) #249/1,449
(249/1449)*100 #17.18427

View(public08NY)

public08IN <- morg08 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public08IN$young <- ifelse(public08IN$age <= 30, 1, 0) 

((sum(public08IN$weight[public08IN$young == 1]))/(sum(public08IN$weight)))*100 #13.76746 #weighted

sum(public08IN$young == 1) #47/395
(47/395)*100 #11.89873 #unweighted

View(public08IN)

public08PA <- morg08 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public08PA$young <- ifelse(public08PA$age <= 30, 1, 0) 

((sum(public08PA$weight[public08PA$young == 1]))/(sum(public08PA$weight)))*100 #14.34522 #weighted

sum(public08PA$young == 1) #97/732
(97/732)*100 #13.25137 #unweighted

View(public08PA)

#2008
############################################ Below is 2009 and above is 2008
#2009

morg09 <- read_csv("data/csv/morg09.csv")

View(public09)

public09IL <- morg09 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public09IL$young <- ifelse(public09IL$age <= 30, 1, 0) 

((sum(public09IL$weight[public09IL$young == 1]))/(sum(public09IL$weight)))*100 #19.51753 #weighted

sum(public09IL$young == 1) #162/905 (# of young people/nobs) 
(162/905)*100 #17.90055 #unweighted

View(public09IL)

public09NY <- morg09 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public09NY$young <- ifelse(public09NY$age <= 30, 1, 0) 

((sum(public09NY$weight[public09NY$young == 1]))/(sum(public09NY$weight)))*100 #18.25429 #weighted

sum(public09NY$young == 1) #251/1496
(251/1496)*100 #16.77807 #unweighted

View(public09NY)

public09IN <- morg09 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public09IN$young <- ifelse(public09IN$age <= 30, 1, 0) 

((sum(public09IN$weight[public09IN$young == 1]))/(sum(public09IN$weight)))*100 #17.32581 #weighted

sum(public09IN$young == 1) #59/409
(59/409)*100 #14.42543 #unweighted

View(public09IN)

public09PA <- morg09 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public09PA$young <- ifelse(public09PA$age <= 30, 1, 0) 

((sum(public09PA$weight[public09PA$young == 1]))/(sum(public09PA$weight)))*100 #19.49671 #weighted

sum(public09PA$young == 1) #128/723
(128/723)*100 #17.70401 #unweighted

View(public09PA)

#2009
############################################ Below is 2010 and above is 2009
#2010

morg10 <- read_csv("data/csv/morg10.csv")

View(public010)

public10IL <- morg10 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public10IL$young <- ifelse(public10IL$age <= 30, 1, 0) 

((sum(public10IL$weight[public10IL$young == 1]))/(sum(public10IL$weight)))*100 #19.71057 #weighted

sum(public10IL$young == 1) #162/905 (# of young people/nobs) 
(162/905)*100 #17.90055 #unweighted

View(public10IL)

public10NY <- morg10 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public10NY$young <- ifelse(public10NY$age <= 30, 1, 0) 

((sum(public10NY$weight[public10NY$young == 1]))/(sum(public10NY$weight)))*100 #18.82587 #weighted

View(public10NY)

public10IN <- morg10 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public10IN$young <- ifelse(public10IN$age <= 30, 1, 0) 

((sum(public10IN$weight[public10IN$young == 1]))/(sum(public10IN$weight)))*100 #17.37014 #weighted

View(public10IN)

public10PA <- morg10 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public10PA$young <- ifelse(public10PA$age <= 30, 1, 0) 

((sum(public10PA$weight[public10PA$young == 1]))/(sum(public10PA$weight)))*100 #18.68248 #weighted

View(public10PA)

#2010
############################################ Below is 2011 and above is 2010
#2011

morg11 <- read_csv("data/csv/morg11.csv")

public11IL <- morg11 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public11IL$young <- ifelse(public11IL$age <= 30, 1, 0) 

((sum(public11IL$weight[public11IL$young == 1]))/(sum(public11IL$weight)))*100 #20.17656 #weighted

View(public11IL)

public11NY <- morg11 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public11NY$young <- ifelse(public11NY$age <= 30, 1, 0) 

((sum(public11NY$weight[public11NY$young == 1]))/(sum(public11NY$weight)))*100 #16.38994 #weighted

View(public11NY)

public11IN <- morg11 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public11IN$young <- ifelse(public11IN$age <= 30, 1, 0) 

((sum(public11IN$weight[public11IN$young == 1]))/(sum(public11IN$weight)))*100 #16.49095 #weighted

View(public11IN)

public11PA <- morg11 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public11PA$young <- ifelse(public11PA$age <= 30, 1, 0) 

((sum(public11PA$weight[public11PA$young == 1]))/(sum(public11PA$weight)))*100 #16.93767 #weighted

View(public11PA)

#2011
############################################ Below is 2012 and above is 2011
#2012

morg12 <- read_csv("data/csv/morg12.csv")

public12IL <- morg12 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public12IL$young <- ifelse(public12IL$age <= 30, 1, 0) 

((sum(public12IL$weight[public12IL$young == 1]))/(sum(public12IL$weight)))*100 #19.69907 #weighted

View(public12IL)

public12NY <- morg12 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public12NY$young <- ifelse(public12NY$age <= 30, 1, 0) 

((sum(public12NY$weight[public12NY$young == 1]))/(sum(public12NY$weight)))*100 #14.93994 #weighted

View(public12NY)

public12IN <- morg12 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public12IN$young <- ifelse(public12IN$age <= 30, 1, 0) 

((sum(public12IN$weight[public12IN$young == 1]))/(sum(public12IN$weight)))*100 #17.57823 #weighted

View(public12IN)

public12PA <- morg12 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public12PA$young <- ifelse(public12PA$age <= 30, 1, 0) 

((sum(public12PA$weight[public12PA$young == 1]))/(sum(public12PA$weight)))*100 #20.1149 #weighted

View(public12PA)

#2012
############################################ Below is 2013 and above is 2012
#2013

morg13 <- read_csv("data/csv/morg13.csv")

public13IL <- morg13 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public13IL$young <- ifelse(public13IL$age <= 30, 1, 0) 

((sum(public13IL$weight[public13IL$young == 1]))/(sum(public13IL$weight)))*100 #20.39708 #weighted

View(public13IL)

public13NY <- morg13 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public13NY$young <- ifelse(public13NY$age <= 30, 1, 0) 

((sum(public13NY$weight[public13NY$young == 1]))/(sum(public13NY$weight)))*100 #14.45421 #weighted

View(public13NY)

public13IN <- morg13 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public13IN$young <- ifelse(public13IN$age <= 30, 1, 0) 

((sum(public13IN$weight[public13IN$young == 1]))/(sum(public13IN$weight)))*100 #18.2969 #weighted

View(public13IN)

public13PA <- morg13 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public13PA$young <- ifelse(public13PA$age <= 30, 1, 0) 

((sum(public13PA$weight[public13PA$young == 1]))/(sum(public13PA$weight)))*100 #13.29593 #weighted

View(public13PA)

#2013
############################################ Below is 2014 and above is 2013
#2014

morg14 <- read_csv("data/csv/morg14.csv")

public14IL <- morg14 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(33))
#now restrict by state, IL = 33

public14IL$young <- ifelse(public14IL$age <= 30, 1, 0) 

((sum(public14IL$weight[public14IL$young == 1]))/(sum(public14IL$weight)))*100 #17.57176 #weighted

View(public14IL)

public14NY <- morg14 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(21))
#now restrict by state, NY = 21

public14NY$young <- ifelse(public14NY$age <= 30, 1, 0) 

((sum(public14NY$weight[public14NY$young == 1]))/(sum(public14NY$weight)))*100 #14.11336 #weighted

View(public14NY)

public14IN <- morg14 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(32))
#now restrict by state, Indiana = 32

public14IN$young <- ifelse(public14IN$age <= 30, 1, 0) 

((sum(public14IN$weight[public14IN$young == 1]))/(sum(public14IN$weight)))*100 #10.00281 #weighted

View(public14IN)

public14PA <- morg14 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(state %in% c(23))
#now restrict by state, PA = 23

public14PA$young <- ifelse(public14PA$age <= 30, 1, 0) 

((sum(public14PA$weight[public14PA$young == 1]))/(sum(public14PA$weight)))*100 #17.96358 #weighted

View(public14PA)

#2014
############################################ Below is 2015 and above is 2014
#2015

morg15 <- read_csv("data/csv/morg15.csv")

public15IL <- morg15 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(stfips %in% c(17))
#now restrict by state, IL = 17 in stfips

public15IL$young <- ifelse(public15IL$age <= 30, 1, 0) 

((sum(public15IL$weight[public15IL$young == 1]))/(sum(public15IL$weight)))*100 #23.60156 #weighted

View(public15IL)

public15NY <- morg15 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(stfips %in% c(36))
#now restrict by state, NY = 36 in stfips

public15NY$young <- ifelse(public15NY$age <= 30, 1, 0) 

((sum(public15NY$weight[public15NY$young == 1]))/(sum(public15NY$weight)))*100 #17.62225 #weighted

View(public15NY)

public15IN <- morg15 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(stfips %in% c(18))
#now restrict by state, Indiana = 18 in stfips

public15IN$young <- ifelse(public15IN$age <= 30, 1, 0) 

((sum(public15IN$weight[public15IN$young == 1]))/(sum(public15IN$weight)))*100 #17.69679 #weighted

View(public15IN)

public15PA <- morg15 |> 
  filter(class94 %in% c( 1,2,3)) |>
  filter(stfips %in% c(42))
#now restrict by state, PA = 42 in stfips

public15PA$young <- ifelse(public15PA$age <= 30, 1, 0) 

((sum(public15PA$weight[public15PA$young == 1]))/(sum(public15PA$weight)))*100 #16.70836 #weighted

View(public15PA)

############################ MAKE GRAPH #######################

library(tibble)

table <- tibble(
  year = 2008:2015,
  "Illinois" = c(18.95, 19.51, 19.71, 20.18, 19.7, 20.4, 17.57, 23.6),
  "New York" = c(18.88, 18.25, 18.83, 16.4, 14.94, 14.45, 14.11, 17.62),
  "Indiana" = c(13.77, 17.33, 17.37, 16.5, 17.58, 18.3, 10, 17.7),
  "Pennsylvania" = c(14.35, 19.5, 18.68, 16.94, 20.11, 13.3, 17.96, 16.71))

View(table)

table2 <- table %>%
  pivot_longer(
    cols = -year,
    names_to = "state",
    values_to = "share_under_30")

View(table2)

library(ggplot2)

ggplot(table2, aes(x = year, y = share_under_30, color = state)) +
  geom_line(size = 1) +
  geom_point() +
  scale_color_brewer(palette = "Set1", name = "State") +
  scale_y_continuous(limits = c(0, NA)) +
  labs(
    title = "Share of Public Employees Age ≤ 30",
    x = "Year",
    y = "Share (Percent)",
    color = "State"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    legend.position = "right",
    plot.title = element_text(face = "bold", size = 16),
    axis.title = element_text(face = "bold"), 
    text = element_text(family = "serif"))


table3 <- tibble()

