# Educational base-R companion for the synthetic Hospital Flow Decision Lab.
# This script is not executed by the hosted Streamlit application.

args <- commandArgs(trailingOnly = TRUE)
csv_path <- if (length(args) >= 1) args[[1]] else "hospital_flow_curated.csv"

flow <- read.csv(csv_path, stringsAsFactors = FALSE)

required <- c(
  "encounter_id", "admission_time", "bed_status", "boarding_hours",
  "occupancy", "admission_volume_24h", "patient_acuity"
)
missing_columns <- setdiff(required, names(flow))
if (length(missing_columns) > 0) {
  stop(paste("Missing required columns:", paste(missing_columns, collapse = ", ")))
}

cat("Rows loaded:", nrow(flow), "\n")
cat("Duplicate encounters:", sum(duplicated(flow$encounter_id)), "\n")
cat("Missing values in required fields:", sum(is.na(flow[required])), "\n\n")

current <- subset(flow, bed_status == "occupied")
current$admission_time <- as.POSIXct(current$admission_time, format = "%Y-%m-%d %H:%M:%S")
current$acuity_score <- unname(c(low = 1, moderate = 2, high = 3)[current$patient_acuity])
current <- current[order(current$admission_time, current$encounter_id), ]

population_z <- function(x, centre, spread) {
  if (spread == 0) return(rep(0, length(x)))
  (x - centre) / spread
}

split_index <- floor(0.70 * nrow(current))
train <- current[seq_len(split_index), ]
test <- current[(split_index + 1):nrow(current), ]
predictors <- c("occupancy", "admission_volume_24h", "acuity_score")

centres <- sapply(train[predictors], mean)
spreads <- sapply(train[predictors], function(x) sqrt(mean((x - mean(x))^2)))

for (name in predictors) {
  train[[name]] <- population_z(train[[name]], centres[[name]], spreads[[name]])
  test[[name]] <- population_z(test[[name]], centres[[name]], spreads[[name]])
}

model <- lm(
  boarding_hours ~ occupancy + admission_volume_24h + acuity_score,
  data = train
)
predictions <- predict(model, newdata = test)
baseline_predictions <- rep(mean(train$boarding_hours), nrow(test))
model_mae <- mean(abs(test$boarding_hours - predictions))
baseline_mae <- mean(abs(test$boarding_hours - baseline_predictions))
test_r_squared <- 1 - sum((test$boarding_hours - predictions)^2) /
  sum((test$boarding_hours - mean(test$boarding_hours))^2)

cat("Time-ordered split: earlier 70% train / latest 30% test\n")
cat("Training rows:", nrow(train), " Test rows:", nrow(test), "\n")
cat("Model MAE:", round(model_mae, 2), "hours\n")
cat("Mean-baseline MAE:", round(baseline_mae, 2), "hours\n")
cat("Test R-squared:", round(test_r_squared, 3), "\n\n")
print(summary(model))

cat("\nInterpretation boundary:\n")
cat("Synthetic exploratory model only; association is not causation, and poor\n")
cat("holdout performance is evidence against operational use without revision.\n")
