import polars as pl

from rich import print
# from rich.console import Console

# Read the data
df = pl.read_csv("data/flipkart_com-ecommerce_sample.csv")
# columns = ['uniq_id', 'crawl_timestamp', 'product_url', 'product_name', 'product_category_tree', 'pid', 'retail_price', 'discounted_price', 'image', 'is_FK_Advantage_product', 'description', 'product_rating', 'overall_rating', 'brand', 'product_specifications']

# drop "crawl_timestamp", "is_FK_Advantage_product"
df = df.drop(["uniq_id", "crawl_timestamp", "is_FK_Advantage_product", "product_specifications", "pid", "overall_rating", "discounted_price"])

# ["Clothing >> Women's Clothing >> Lingerie, Sleep & Swimwear >> Shorts >> Alisha Shorts >> Alisha Solid Women's Cycling Shorts"]
# split categories, strip the extra spaces and store in list

df = df.with_columns([
    pl.col('product_category_tree')
    .str.replace_all(r'[\[\]"]', '')  # Remove brackets and quotes
    .str.split(">>")  # Split on '>>'
    .map_elements(lambda x: [category.strip() for category in x],
                 return_dtype=pl.List(pl.Utf8))  # Specify return type
    .alias('product_category_tree')
])

df = df.with_columns([
    pl.col("image")
    .str.replace_all(r'[\[\]"]', '')  # Remove brackets and quotes
    .str.split(",")  # Split on ','
    .map_elements(lambda x: [url.strip() for url in x],
                 return_dtype=pl.List(pl.Utf8))  # Specify return type
    .alias("image")
])


records = df.to_dicts()

print(df.head(5))
print(df.columns)
print(records[0])
import json

with open("data/flipkart_data.json", "w") as f:
    json.dump(records, f, indent=4)