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
