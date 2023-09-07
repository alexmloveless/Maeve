## Usage

```python
from maeve.session import Session
s = Session(log_level="DEBUG")
# invoke a plugin e.g.
data = s.create("Data") # or "data"
```
- A plugin can also be an external module or package
- Session passes itself to plugin
- All internal shareable state for plugin is stored in session
  - This includes datasets
- We probably want to create a package of generic helper functions that is included in the session namespace by default
- I think it should also be the case that stuff can be imported from plugins without invoking the constructor, although I'm not sure how this would work