# jupyTango - The Swiss Army Knife for the common Tango Controls user

Dear friends of Tango Controls.

It is time to share with you what is one my my favourite tools for Tango Controls: [jupyTango](https://gitlab.com/tango-controls/jupytango) We had the jupyTango workshop at the HQ in September 2022. Bunt in case you missed it, the movie below shows attribute plots being updated in realtime in a Jupyter Notebook. Yep, that's one of the outstanding features of jupyTango.

 <video src="Screen Recording 2022-12-14 at 14.27.51.mov"></video>

## Requirements

Among other things you will need a local Tango Controls installation with a recent PyTango, preferrably >=9.5.0. But do not worry, it is all going to be very simple. So let's walk through the prerequisites together.

1. **Please make certain that you have a VENV active! Better be safe than sorry.** If you have no virtual environment yet, you can create one quite easily in the directory `.venv`:

    ```bash
    python3 -m venv --upgrade-deps .venv
    ```

2. Now install PyTango and iTango in the virtual environment:
    ```bash
    python3 -m pip --require-virtualenv pytango itango
    ```

3. jupyTango leverages an existing iTango profile. Therefore, in order to be able to copy an existing iTango profile to a new jupyTango profile, you have to have an iTango profile already in place. If you don't have an iTango profile yet, either run iTango at least once or you could try and use an existing iPython profile **after** you have run iPython at least once.

##Installation

Once you have an iTango or iPython profile, continue with the jupyTango installation:

```
# Clone the jupyTango repo and cd to it.
git clone --recurse-submodules --shallow-submodules https://gitlab.com/tango-controls/jupytango.git
cd jupytango

# Install jupyTango in the venv. You created a venv, right?
python3 -m pip --require-virtualenv install .

# Copy an existing iTango profile to become the new jupyTango profile.
cp -Rf ${HOME}/.ipython/profile_tango ${HOME}/.ipython/profile_jupytango

# Add to the profile to load jupyTango.
echo "c.InteractiveShellApp.extensions = ['jupytango']" >> ${HOME}/.ipython/profile_jupytango/ipython_config.py

# Install the Jupyter kernel for the jupyTango profile in the venv.
python3 -m ipykernel install --prefix ${VIRTUAL_ENV} --name jupyTango --display-name "jupyTango" --profile jupytango

# Copy some decorative files over
cp resources/logo/* ${VIRTUAL_ENV}/share/jupyter/kernels/jupytango

# Start Jupyter lab. This will open a browser tab/window.
jupyter-lab --ip 0.0.0.0
```

Yes, it really is that simple. Enjoy!