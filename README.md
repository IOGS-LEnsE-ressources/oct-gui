# oct-gui

**OCT-Gui** is a complete graphical user interface (based on PyQt6) dedicated to labworks about **OCT** microscopy at the Experimental Teaching Laboratory (LEnsE) of the Institut d'Optique Graduate School (IOGS).

![View of the interface](docs/source/_static/images/interface_main.png)

## Main contributors

This Python/PyQt6 release of the GUI was developed by **Noam CHOPPINET** (Student at Institut d’Optique from 2024 to 2027) during an internship in July 2025.

This release was made under the supervision of **Julien MOREAU** (Professor at Institut d’Optique) and **Julien VILLEMEJANE** (Teacher at Institut d’Optique).

*This GUI is based on an obsolete LabView version, developed by Julien MOREAU (and students).*

Technical support was regularly provided by Thierry AVIGNON (Lead Technical and Operations Engineer at LEnsE / Institut d’Optique).




## Context

**Optical Coherence Tomography (OCT)** is a microscopy technique designed to image deep within scattering samples. This represents a major challenge in biophotonics, where virtually all samples—whether *in vivo* or *in vitro*—are highly scattering and absorbing. 

One of the main medical applications of OCT is corneal imaging, using devices commonly found in ophthalmology clinics. Another notable example is an ongoing clinical study on skin cancer detection, using an OCT device developed by alumni of the Institut d’Optique.

## Experimental Setup

## Main Algorithm of the application



![Main algorithm](docs/source/_static/images/oct_main_algo.png)



## How to use this repository

You can Download or Clone this repository.

Then, you have to go to the **appli** directory and start the application by the following instruction:

'''
python oct_lab_app.py
'''

## Requirements

This application is coded in **Python** (3.10 or more) and it is based on **PyQt6**.

To be used with the OCT interferometer system, you need to install specific drivers and Python API for a *Basler* 
USB camera. Piezo and stepper modules are controlled by Thorlabs Kinesis drivers that requires also *pythonnet* package.

Other libraries or packages are required. You can access to the list in the *requirements.txt* file, from the **appli** directory.