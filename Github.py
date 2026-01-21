# Databricks notebook source
git config --global user.name 'ABeverton'
git config --global user.email 'andy.beverton@environment-agency.gov.uk'

# COMMAND ----------

dbutils.fs.mkdirs("/mnt/lab/unrestricted/andy.beverton@environment-agency.gov.uk") 

# COMMAND ----------

#…or create a new repository on the command line
echo "# Denver-Complex" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/ABeverton/Denver-Complex.git
git push -u origin main

# COMMAND ----------

#…or push an existing repository from the command line
git remote add origin https://github.com/ABeverton/Denver-Complex.git
git branch -M main
git push -u origin main
