# Setting up PyOpenGL

```Bash
pip install pyopengl
```

Running on `pyenv`:

```
vim ~/.pyenv/versions/3.8.2/lib/python3.8/site-packages/OpenGL/platform/ctypesloader.py
```

Change the line:
```Python
fullName = util.find_library( name )
# to
fullName = '/System/Library/Frameworks/OpenGL.framework/OpenGL'
```
