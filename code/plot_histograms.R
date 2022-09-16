# Load packages
library(here)
library(tidyverse)

# Plot histogram for language meta-analysis
language_experiments <- here("data", "language_experiments.csv") %>%
    read_csv(col_types = cols())
language_gm_age <- with( # Grand mean age
    language_experiments, sum(mean_age * sample_size) / sum(sample_size)
)
(language_plot <- language_experiments %>%
    arrange(desc(sample_size)) %>%
    mutate(
        xmin = floor(mean_age),
        xmax = xmin + 1
    ) %>%
    group_by(xmin) %>%
    mutate(ymin = row_number(), ymax = ymin + 1) %>%
    ggplot() +
    annotate(
        geom = "segment", x = language_gm_age, xend = language_gm_age,
        y = 1.0, yend = 8.0, color = "gray70", size = 0.8
    ) +
    annotate(
        geom = "text", x = language_gm_age - 0.2, y = 7.54,
        label = paste0("Grand mean\n", round(language_gm_age, 2), " years"),
        color = "gray60", hjust = 1.0
    ) +
    geom_rect(
        aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax),
        color = "white", fill = "#b4cce6", size = 1.0
    ) +
    geom_point(
        aes(x = xmin + 0.5, y = ymin + 0.5, size = sample_size),
        color = "#0e60b0"
    ) +
    scale_size(
        range = c(1, 10),
        guide = guide_legend(title.position = "top", title.hjust = 0.5)
    ) +
    scale_x_continuous(breaks = 4:13) +
    coord_equal() +
    labs(x = "Mean age (years)", size = "Sample size") +
    theme_void() +
    theme(
        legend.direction = "vertical",
        legend.position = c(0.14, 0.72),
        axis.text.x = element_text(vjust = 4.0),
        axis.title.x = element_text(vjust = 2.0),
        panel.background = element_rect(color = NA, fill = "white"),
        plot.background = element_rect(color = NA, fill = "white")
    ))

# Save
ggsave(
    here("figures", "language_histogram.png"), language_plot,
    width = 5.0, height = 4.0
)

# Plot histogram for semantics meta-analysis
semantics_experiments <- here("data", "semantics_experiments.csv") %>%
    read_csv(col_types = cols())
semantics_gm_age <- with( # Grand mean age
    semantics_experiments, sum(mean_age * sample_size) / sum(sample_size)
)
(semantics_plot <- semantics_experiments %>%
    arrange(desc(sample_size)) %>%
    mutate(xmin = floor(mean_age / 0.5) * 0.5, xmax = xmin + 0.5) %>%
    group_by(xmin) %>%
    mutate(ymin = row_number(), ymax = ymin + 1) %>%
    ggplot() +
    annotate(
        geom = "segment", x = semantics_gm_age, xend = semantics_gm_age,
        y = 1.0, yend = 8.0, color = "gray70", size = 0.8
    ) +
    annotate(
        geom = "text", x = semantics_gm_age - 0.1, y = 7.54,
        label = paste0("Grand mean\n", round(semantics_gm_age, 2), " years"),
        color = "gray60", hjust = 1.0
    ) +
    geom_rect(
        aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax),
        color = "white", fill = "#b4cce6", size = 1.0
    ) +
    geom_point(
        aes(x = xmin + 0.25, y = ymin + 0.5, size = sample_size),
        color = "#0e60b0"
    ) +
    scale_size(
        range = c(1, 10),
        guide = guide_legend(title.position = "top", title.hjust = 0.5)
    ) +
    scale_x_continuous(breaks = seq(5.5, 13.0, 0.5)) +
    coord_fixed(ratio = 0.5) +
    labs(x = "Mean age (years)", size = "Sample size") +
    theme_void() +
    theme(
        legend.direction = "vertical",
        legend.position = c(0.10, 0.79),
        axis.text.x = element_text(vjust = 4.0),
        axis.title.x = element_text(vjust = 2.0),
        panel.background = element_rect(color = NA, fill = "white"),
        plot.background = element_rect(color = NA, fill = "white")
    ))

# Save
ggsave(
    here("figures", "semantics_histogram.png"), semantics_plot,
    width = 8.0, height = 4.0
)
