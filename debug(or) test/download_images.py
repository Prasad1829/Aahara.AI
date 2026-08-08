from icrawler.builtin import BingImageCrawler

classes = [
    "cabbage", "capsicum", "carrot", "cauliflower", "chicken",
    "cucumber", "egg", "eggplant", "fish", "garlic",
    "ginger", "lemon", "okra", "onion", "paneer",
    "peas", "potato", "rice", "spinach", "tomato",
]

for cls in classes:
    print(f"Downloading: {cls}")
    crawler = BingImageCrawler(storage={"root_dir": f"dataset/{cls}"})
    crawler.crawl(keyword=f"raw {cls} ingredient", max_num=220)
