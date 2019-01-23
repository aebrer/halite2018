library(tidyverse)
library(ggthemes)  # not needed but nice perk

mydata <- read_csv("map_before.csv", col_names = c("x", "y", "score", "type", "turn"))
mydata <- mydata %>%
  group_by(type, turn) %>%
  mutate(norm_score = score / max(score)) %>%
  filter((turn - 1) %% 50 == 0)

# final heatmap
ggplot(mydata, aes(x = x, y = y, fill = score)) +
  geom_tile(stat = "identity", color = "white") +
  scale_fill_distiller(type = "seq", palette = "YlOrRd") +
  theme_tufte() +
  facet_grid(turn~type, scales = "free")
ggsave("map_kernel_wrap.png", height = 20, width = 6, limitsize = F)
