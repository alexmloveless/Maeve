# Maeve - data done quick!

Maeve is a data science toolkit and workflow management tool optimised for fast analysis, visualisation and prototyping in novel data environments built in pure python using Pandas as its primary means of handling data (more back end to come!)

Maeve is made for small teams of itinerant data scientists and analysts who need to get up and running quickly in new data environments while having a familiar, portable toolset, and ease of sharing of data access and processing and analysis pipelines. Since only Python is required, it should be acceptable and functional in all but the most restrictive IT environments. We try to keep dependencies to a minimum in case there's a need to use an organisation's hardware which may have restrictive installation policies. Maeve is at her best when run from a centralised, version-controlled (H)JSON configuration (recipe) repository but is also implemented as a Pandas extension so that many of the functions and recipes can be called as part of functional chains like any other Pandas method.

Meave is still very much is the development, pre-alpha phase. She is functional and useful but will be a bit creaky and inconsistent in places, and wildly incomplete in others!

## Usage

```python
from maeve import Session
me = Session(conf="/path/to/conf/")
obj = me.cook("MyRecipe")
```
Try the demo! .
```python
from maeve import Session
me = Session()
obj = me.cook("Yummy")
```
This will load a Pandas DataFrame.

Maeve cooks up tasty data dishes using what are called "recipes" which are formulae created using (H)JSON which feed instractuctions to Maeve. Check out the recipe for Yummy:

```python
print(me.recipes.pretty_print_conf("Yummy"))
```
Which returns a dict:
```json
{
    "recipe_type": "data",
    "metadata": {
        "conf_file": "/Users/alex/Dropbox/Projects/pypackages/Maeve/maeve/recipebook/demo_recipes/demos.hjson",
        "loaded": "2023-09-30 20:48:56"
    },
    "backend": "pandas",
    "load": {
        "function": "read_csv",
        "location": {
            "recipe_type": "location",
            "use_path": "_package_root",
            "path": "/Users/alex/Dropbox/Projects/pypackages/Maeve/maeve/recipebook/demo_files/yummy.csv",
            "orig_path": "recipebook/demo_files/yummy.csv",
            "paths": {
                "test_data": "/Users/alex/Dropbox/Projects/pypackages/Maeve/tests/data/data"
            }
        }
    }
}
```
But that's not actually what the recipe looks like in its raw form, some culinary magic has happened! Let's look at the recipe before it gets embelished:

```python
print(me.recipes.pretty_print_conf("Yummy", resolve=False))
```
Now we can see under the hood:
```json
{
    "backend": "pandas",
    "recipe_type": "data",
    "load": {
        "function": "read_csv",
        "location": "@YummyCSV"
    },
    "metadata": {
        "conf_file": "/Users/alex/Dropbox/Projects/pypackages/Maeve/maeve/recipebook/demo_recipes/demos.hjson",
        "loaded": "2023-09-30 20:53:11"
    }
}
```
Actually, the metadata bit was added by Maeve. The actual recipe is just the other 3 fields!
