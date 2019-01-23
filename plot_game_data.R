library(tidyverse)
library(ggthemes)  # not needed but nice perk


mydata <- read_tsv("game_data.tsv", col_names = c("turn", "var", "val"))
mydata$val <- as.numeric(mydata$val)
mydata <- mydata %>%
  spread(var, val)

ggplot(mydata) +
  geom_point(aes(y=runtime, x=my_ships)) +
  geom_smooth(aes(y=runtime, x=my_ships), method = "lm") +
  theme_minimal()

ggplot(mydata, aes(x=turn)) +
  # geom_line(aes(y=spaces_per_all_ships)) +
  geom_line(aes(y=num_eligible_spaces)) +
  # geom_line(aes(y=my_ships)) +
  # geom_line(aes(y=geo_mean_ships)) +
  theme_minimal() +
  ylim(c(0, 2000))

ggplot(mydata, aes(x=turn)) +
  geom_line(aes(y=spaces_per_all_ships), color="red") +
  geom_line(aes(y=ship_spawn_space_cutoff), color="blue") +
  geom_line(aes(y=total_ships)) +
  geom_line(aes(y=my_ships), color="green", size=2) +
  geom_line(aes(y=mean_ships), color="purple") +
  geom_line(aes(y=geo_mean_ships), color="yellow") +
  theme_minimal() +
  ylim(c(0, 100))

ggplot(mydata, aes(x=turn)) +
  geom_line(aes(y=halite_ratio), color="red") +
  geom_point(aes(y=progress_ratio), color="blue") +
  geom_line(aes(y=turn_ratio), color="green") +
  theme_minimal() +
  ylim(c(0, 1))


ggplot(mydata, aes(x=turn)) +
  geom_line(aes(y=collect_percentile), color="red3") +
  geom_line(aes(y=target_percentile), color="blue3") +
  geom_point(aes(y=collect_minimum), color="red1") +
  geom_point(aes(y=target_minimum), color="blue1") +
  theme_minimal() +
  ylim(c(0, 120))

ggplot(mydata) +
  # geom_point(aes(x=halite_ratio, y=ship_spawn_space_cutoff)) +
  geom_point(aes(x=progress_ratio, y=ship_spawn_space_cutoff)) +
  theme_minimal()






ggplot(mydata, aes(x=turn)) +
  geom_line(aes(y=spaces_per_all_ships), color="red") +
  geom_line(aes(y=ship_spawn_space_cutoff), color="blue") +
  geom_line(aes(y=((total_ships - my_ships) * 3))) +
  geom_line(aes(y=my_ships), color="green", size=2) +
  geom_line(aes(y=mean_ships), color="purple") +
  geom_line(aes(y=target_minimum), color="yellow") +
  theme_minimal() +
  ylim(c(0, 100))

ggplot(mydata, aes(x=turn)) +
  geom_line(aes(y=ship_spawn_space_cutoff), color="blue") +
  geom_line(aes(y=((total_ships - my_ships) * 3)), color="purple") +
  geom_line(aes(y=total_ships - my_ships), color="orange") +
  geom_line(aes(y=total_ships), color="black") +
  geom_line(aes(y=my_ships), color="green", size=2) +
  geom_line(aes(y=mean_ships), color="red") +
  theme_minimal() +
  ylim(c(0,200))





mydata <- read_tsv("figure_out_shit.tsv", col_names = c("var", "timepoint", "value", "gametype"))
mydata_stats <- mydata %>%
  group_by(var, timepoint) %>%
  summarize(mean_value = mean(value))
mydata_wide <- mydata %>%
  spread(gametype, value)
