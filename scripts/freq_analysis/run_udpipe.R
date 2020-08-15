# Set the CRAN mirror
r <- getOption("repos")
r["CRAN"] <- "http://cran.us.r-project.org"
options(repos = r)

# List the required packages (fragile, this requires manual updating)
pkgs <- c(
  "udpipe",
  "data.table",
  "tidyverse"
)

# Define a helper function to check if the package is installed
install <- function(pkg) {
  if (!require(pkg, character.only = TRUE)) {
    warning(sprintf("Package %s not installed. Installing from CRAN...", pkg))
    install.packages(pkg)
  } else {
    message(sprintf("Package %s already installed.", pkg))
  }
}

# Install each package
lapply(pkgs, install)

###
library(udpipe)
library(tidyverse)

args = commandArgs(trailingOnly=TRUE)
print(args)

stopifnot(length(args) == 3)

df <- read_csv(args[1])
num_cpu <- args[2]
out_fname <- args[3]

df_es <- filter(df, lang == "es")
df_en <- filter(df, lang == "en")

#path_es <- "./spanish-lemma-model.udpipe"
#path_en <- "./english-lemma-model.udpipe"
#if (!file.exists(path_es)) {
#    model_es <- udpipe_download_model(language = "spanish", model_dir = path_es)
#}

#if (!file.exists(path_en)) {
#    model_en <- udpipe_download_model(language = "spanish", model_dir = path_en)
#}

model_en <- udpipe_load_model("./english-lemma-model.udpipe/english-ewt-ud-2.4-190531.udpipe")
model_es <- udpipe_load_model("./english-lemma-model.udpipe/spanish-gsd-ud-2.4-190531.udpipe")

x <- data.frame(doc_id = df_es$X1, text = df_es$text, stringsAsFactors = FALSE)
print("running udpipe es now..")
results_es <- data.frame(udpipe(x, model_es, parallel.cores = num_cpu))

x <- data.frame(doc_id = df_en$X1, text = df_en$text, stringsAsFactors = FALSE)
print("running udpipe en now..")
results_en <- data.frame(udpipe(x, model_en, parallel.cores = num_cpu))

replace_na <- function(x) {
    if (x == "na") {
        return("")
    }
    return(x)
}

lemma_df <- rbind(results_es, results_en) %>%
    select(doc_id, lemma) %>%
    group_by(doc_id) %>%
    transmute(text = paste0(lemma, collapse = " ")) %>%
    distinct() %>%
    transmute(text = replace_na(text))

df <- mutate(df, text = lemma_df$text) %>%
    select(-X1)

write_csv(df, out_fname)
print("finished running udpipe")
